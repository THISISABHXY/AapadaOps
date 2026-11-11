"""AapadaOps Operational Operations-Research Optimization Engine.

Formulates and solves multi-criteria Mixed-Integer Linear Programs (MIP) using Google OR-Tools
to recommend optimal tactical forces and disaster equipment for emergency response.
Produces multiple feasible tactical recommendations with explainable trade-offs.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from ortools.linear_solver import pywraplp
from app.coordination.schemas import (
    OptimizationRequest,
    OptimizationResponse,
    RecommendationOption,
    ResourceEntityView,
    ResponseTeamEntityView,
)
from app.models.incident import IncidentCategory
from app.models.resource import Resource, ResourceStatus, ResourceType
from app.models.team import ResponseTeam, TeamStatus
from app.services.spatial_service import haversine_distance_meters

logger = logging.getLogger("aapadaops.coordination.optimizer")

# Standard transit velocity assumptions (rural Odisha disaster terrain)
PAVED_ROAD_KMH = 40.0  # Average speed on rural highways / MDRs
FLOOD_APPROACH_KMH = 15.0  # Speed in partially submerged approach sectors
AMPHIBIOUS_LAUNCH_DELAY_MINUTES = 20.0  # Time required to stage and launch motorized inflatable boats


def team_to_view(t: ResponseTeam) -> ResponseTeamEntityView:
    """Safely convert ORM ResponseTeam to ResponseTeamEntityView schema."""
    return ResponseTeamEntityView(
        id=t.id or "TEAM",
        code=t.code,
        name=t.name,
        organization=t.organization,
        battalion=t.battalion,
        team_lead_name=t.team_lead_name,
        team_lead_phone=t.team_lead_phone,
        total_personnel=t.total_personnel,
        specialization=getattr(t, "specialization", None) or "WATER_RESCUE",
        rescue_capacity_persons=getattr(t, "rescue_capacity_persons", None) or 30,
        current_district_name=t.current_district_name,
        status=t.status,
        latitude=t.latitude,
        longitude=t.longitude,
        assigned_incident_id=getattr(t, "assigned_incident_id", None),
        assigned_plan_id=getattr(t, "assigned_plan_id", None),
        last_updated_time=getattr(t, "updated_at", None) or datetime.now(timezone.utc),
    )


def resource_to_view(r: Resource) -> ResourceEntityView:
    """Safely convert ORM Resource to ResourceEntityView schema."""
    return ResourceEntityView(
        id=r.id or "RES",
        code=r.code,
        name=r.name,
        category=r.category,
        organization=r.organization,
        district_name=r.district_name,
        status=r.status,
        quantity=r.quantity,
        capacity=getattr(r, "capacity", None) or 10,
        capacity_unit=getattr(r, "capacity_unit", None) or "units",
        latitude=r.latitude,
        longitude=r.longitude,
        assigned_incident_id=getattr(r, "assigned_incident_id", None),
        assigned_plan_id=getattr(r, "assigned_plan_id", None),
        last_updated_time=getattr(r, "updated_at", None) or datetime.now(timezone.utc),
    )


class ResponseOptimizationEngine:
    """Operations Research solver using Google OR-Tools MIP (SCIP/CBC)."""

    @classmethod
    def _calculate_transit_time(
        cls,
        distance_km: float,
        road_severed: bool = False,
        is_coastal_surge: bool = False,
    ) -> float:
        """Calculate calculated estimated transit time in minutes.

        Explicitly marked as calculated estimate (not real-time GPS telemetry).
        """
        # Distance travel time at 40 km/h
        transit_mins = (distance_km / PAVED_ROAD_KMH) * 60.0

        if road_severed:
            transit_mins += AMPHIBIOUS_LAUNCH_DELAY_MINUTES

        if is_coastal_surge:
            transit_mins += 15.0

        # Enforce realistic minimum mobilization window
        return round(max(15.0, transit_mins), 1)

    @classmethod
    def _calculate_team_affinity(
        cls,
        team: ResponseTeam,
        category: IncidentCategory,
    ) -> float:
        """Score how well a team's capabilities match the incident disaster type (0.0 to 1.0)."""
        specialization = (getattr(team, "specialization", None) or "WATER_RESCUE").upper()
        org = (getattr(team, "organization", None) or "ODRAF").upper()

        if category in (IncidentCategory.FLOOD, IncidentCategory.EMBANKMENT_BREACH, IncidentCategory.STRANDED_PERSONS):
            if "WATER" in specialization or "ODRAF" in org or "NDRF" in org:
                return 1.0
            if "FIRE" in org:
                return 0.75
            return 0.50

        if category in (IncidentCategory.TREE_FALL, IncidentCategory.ROAD_BLOCK):
            if "TREE" in specialization or "FIRE" in org:
                return 1.0
            if "ODRAF" in org:
                return 0.80
            return 0.40

        if category == IncidentCategory.MEDICAL_EMERGENCY:
            if "MEDICAL" in specialization or "HEALTH" in org:
                return 1.0
            if "ODRAF" in org or "NDRF" in org:
                return 0.70
            return 0.50

        return 0.60

    @classmethod
    def generate_recommendations(
        cls,
        req: OptimizationRequest,
        available_teams: List[ResponseTeam],
        available_resources: List[Resource],
    ) -> OptimizationResponse:
        """Formulate and solve multi-objective resource allocation optimization using OR-Tools."""
        if not available_teams and not available_resources:
            return OptimizationResponse(
                incident_id=req.incident_id,
                recommendations=[],
                solver_engine="Google OR-Tools MIP Solver",
            )

        recommendations: List[RecommendationOption] = []

        # -------------------------------------------------------------
        # Strategy A: MINIMAL_TIME (Fastest Tactical Arrival)
        # -------------------------------------------------------------
        strat_a = cls._solve_minimal_time(req, available_teams, available_resources)
        if strat_a:
            recommendations.append(strat_a)

        # -------------------------------------------------------------
        # Strategy B: MAXIMAL_CAPACITY (Heavy Coordinated Staging)
        # -------------------------------------------------------------
        strat_b = cls._solve_maximal_capacity(req, available_teams, available_resources)
        if strat_b:
            recommendations.append(strat_b)

        # -------------------------------------------------------------
        # Strategy C: RESERVE_PRESERVATION (Strategic Mutual Aid)
        # -------------------------------------------------------------
        strat_c = cls._solve_reserve_preservation(req, available_teams, available_resources)
        if strat_c:
            recommendations.append(strat_c)

        return OptimizationResponse(
            incident_id=req.incident_id,
            recommendations=recommendations[: req.max_recommendations],
            solver_engine="Google OR-Tools Mixed-Integer Programming (SCIP Solver)",
        )

    @classmethod
    def _solve_minimal_time(
        cls,
        req: OptimizationRequest,
        teams: List[ResponseTeam],
        resources: List[Resource],
    ) -> Optional[RecommendationOption]:
        """OR-Tools MIP: Minimizes arrival time using closest qualified tactical unit."""
        solver = pywraplp.Solver.CreateSolver("SCIP")
        if not solver or not teams:
            return None

        # Calculate distances & transit times
        team_data: List[Tuple[ResponseTeam, float, float]] = []
        for t in teams:
            dist_km = haversine_distance_meters(req.target_latitude, req.target_longitude, t.latitude, t.longitude) / 1000.0
            eta_mins = cls._calculate_transit_time(dist_km, req.road_access_severed, req.is_coastal_surge)
            team_data.append((t, dist_km, eta_mins))

        # Binary decision variables x_i: 1 if team i is dispatched, 0 otherwise
        x = [solver.BoolVar(f"team_{i}") for i in range(len(teams))]

        # Objective: Minimize weighted ETA minus affinity bonus
        objective = solver.Objective()
        for i, (t, dist_km, eta_mins) in enumerate(team_data):
            affinity = cls._calculate_team_affinity(t, req.category)
            # Cost = transit minutes scaled by (2.0 - affinity)
            cost = eta_mins * (1.8 - affinity * 0.8)
            objective.SetCoefficient(x[i], cost)
        objective.SetMinimization()

        # Constraint: Dispatch at least 1 team (and at most 1 primary lead team for Strategy A)
        solver.Add(solver.Sum(x) == 1)

        status = solver.Solve()
        if status not in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE):
            return None

        selected_teams = [team_data[i][0] for i in range(len(teams)) if x[i].solution_value() > 0.5]
        if not selected_teams:
            return None

        lead_team = selected_teams[0]
        lead_dist = next(d for t, d, _ in team_data if t.id == lead_team.id)
        lead_eta = next(e for t, _, e in team_data if t.id == lead_team.id)

        # Match relevant resources near incident or near team station
        chosen_resources = []
        for r in resources:
            r_dist = haversine_distance_meters(req.target_latitude, req.target_longitude, r.latitude, r.longitude) / 1000.0
            # Include boats for water rescue or pumps/saws matching category
            if req.category in (IncidentCategory.FLOOD, IncidentCategory.EMBANKMENT_BREACH, IncidentCategory.STRANDED_PERSONS):
                if r.category in (ResourceType.INFLATABLE_BOAT, ResourceType.POWER_BOAT) and r_dist < 45.0:
                    chosen_resources.append(r)
            elif req.category in (IncidentCategory.TREE_FALL, IncidentCategory.ROAD_BLOCK):
                if r.category == ResourceType.JCB_EXCAVATOR and r_dist < 35.0:
                    chosen_resources.append(r)
            if len(chosen_resources) >= 2:
                break

        total_personnel = lead_team.total_personnel
        rescue_cap = getattr(lead_team, "rescue_capacity_persons", 30)

        reasoning = (
            f"Optimized for rapid on-site arrival: Dispatches {lead_team.name} ({lead_team.organization}) "
            f"located {round(lead_dist, 1)} km from target village {req.target_village}. "
            f"Delivers earliest estimated arrival window of {int(lead_eta)} minutes."
        )

        assumptions = [
            f"Assumes uninterrupted transit along primary road network at ~{int(PAVED_ROAD_KMH)} km/h.",
            "Vehicle movement model is a calculated estimate; does not reflect live satellite telemetry.",
            "Assumes local station lead confirms dispatch order within standard 10-minute SLA.",
        ]

        limitations = [
            f"Single-unit deployment capacity ({rescue_cap} persons) may require secondary waves if stranded headcount exceeds initial estimates.",
            f"Does not utilize inter-district mutual aid.",
        ]

        impact = {
            "target_district": req.target_district,
            "local_station_depletion_percent": 33.0,
            "estimated_wave_capacity": rescue_cap,
            "estimated_arrival_window_minutes": int(lead_eta),
        }

        score = max(50.0, min(98.0, 100.0 - (lead_eta * 0.5)))

        return RecommendationOption(
            strategy_id="MINIMAL_TIME",
            title="Rapid Tactical Strike (Minimal Arrival Time)",
            recommended_teams=[team_to_view(t) for t in selected_teams],
            recommended_resources=[resource_to_view(r) for r in chosen_resources],
            total_personnel_deployed=total_personnel,
            total_rescue_capacity_persons=rescue_cap,
            estimated_distance_km=round(lead_dist, 1),
            estimated_arrival_minutes=lead_eta,
            telemetry_source="CALCULATED_ESTIMATE",
            is_live_telemetry=False,
            reasoning=reasoning,
            assumptions=assumptions,
            limitations=limitations,
            estimated_resource_impact=impact,
            optimization_score=round(score, 1),
        )

    @classmethod
    def _solve_maximal_capacity(
        cls,
        req: OptimizationRequest,
        teams: List[ResponseTeam],
        resources: List[Resource],
    ) -> Optional[RecommendationOption]:
        """OR-Tools MIP: Maximizes total rescued headcount capacity while bounding maximum transit time."""
        solver = pywraplp.Solver.CreateSolver("SCIP")
        if not solver or len(teams) < 1:
            return None

        team_data: List[Tuple[ResponseTeam, float, float, int]] = []
        for t in teams:
            dist_km = haversine_distance_meters(req.target_latitude, req.target_longitude, t.latitude, t.longitude) / 1000.0
            eta_mins = cls._calculate_transit_time(dist_km, req.road_access_severed, req.is_coastal_surge)
            cap = getattr(t, "rescue_capacity_persons", 30)
            team_data.append((t, dist_km, eta_mins, cap))

        x = [solver.BoolVar(f"team_{i}") for i in range(len(teams))]

        # Objective: Maximize total rescue capacity while penalizing transit time
        objective = solver.Objective()
        for i, (t, dist_km, eta_mins, cap) in enumerate(team_data):
            # Benefit = capacity points minus slight delay penalty
            benefit = cap - (eta_mins * 0.2)
            objective.SetCoefficient(x[i], benefit)
        objective.SetMaximization()

        # Constraints:
        # Select 2 teams if available, else 1
        num_teams_to_pick = min(2, len(teams))
        solver.Add(solver.Sum(x) == num_teams_to_pick)

        # Transit time bound: individual team transit must be under 120 minutes
        for i, (_, _, eta_mins, _) in enumerate(team_data):
            solver.Add(x[i] * int(eta_mins) <= 120)

        status = solver.Solve()
        if status not in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE):
            return None

        selected_teams = [team_data[i][0] for i in range(len(teams)) if x[i].solution_value() > 0.5]
        if not selected_teams:
            return None

        total_personnel = sum(t.total_personnel for t in selected_teams)
        total_cap = sum(getattr(t, "rescue_capacity_persons", 30) for t in selected_teams)
        max_dist = max(haversine_distance_meters(req.target_latitude, req.target_longitude, t.latitude, t.longitude) / 1000.0 for t in selected_teams)
        max_eta = max(cls._calculate_transit_time(haversine_distance_meters(req.target_latitude, req.target_longitude, t.latitude, t.longitude) / 1000.0, req.road_access_severed, req.is_coastal_surge) for t in selected_teams)

        # Allocate matching equipment (boats, pumps, etc.)
        chosen_resources = []
        for r in resources:
            if req.category in (IncidentCategory.FLOOD, IncidentCategory.EMBANKMENT_BREACH, IncidentCategory.STRANDED_PERSONS):
                if r.category in (ResourceType.INFLATABLE_BOAT, ResourceType.POWER_BOAT):
                    chosen_resources.append(r)
            elif req.category in (IncidentCategory.TREE_FALL, IncidentCategory.ROAD_BLOCK):
                if r.category in (ResourceType.JCB_EXCAVATOR, ResourceType.POWER_BOAT):
                    chosen_resources.append(r)
            if len(chosen_resources) >= 3:
                break

        reasoning = (
            f"Optimized for high-capacity mass rescue: Commits {len(selected_teams)} tactical units "
            f"({', '.join(t.name for t in selected_teams)}) delivering a combined rescue capacity of "
            f"{total_cap} individuals in a coordinated deployment."
        )

        assumptions = [
            "Assumes joint staging area established at block headquarters.",
            "Calculated transit times assume standard road passage without complete bridge collapse.",
            "Requires simultaneous deployment approval by District Disaster Management Authority (DDMA).",
        ]

        limitations = [
            f"Heavier resource commitment: Depletes {int(len(selected_teams)*30)}% of regional tactical response personnel.",
            f"Later arrival wave (~{int(max_eta)} mins) compared to single rapid scout unit.",
        ]

        impact = {
            "target_district": req.target_district,
            "local_station_depletion_percent": 65.0,
            "estimated_wave_capacity": total_cap,
            "estimated_arrival_window_minutes": int(max_eta),
        }

        score = max(55.0, min(95.0, 75.0 + (total_cap * 0.2) - (max_eta * 0.15)))

        return RecommendationOption(
            strategy_id="MAXIMAL_CAPACITY",
            title="Heavy Staging & Evacuation (Maximal Capacity)",
            recommended_teams=[team_to_view(t) for t in selected_teams],
            recommended_resources=[resource_to_view(r) for r in chosen_resources],
            total_personnel_deployed=total_personnel,
            total_rescue_capacity_persons=total_cap,
            estimated_distance_km=round(max_dist, 1),
            estimated_arrival_minutes=max_eta,
            telemetry_source="CALCULATED_ESTIMATE",
            is_live_telemetry=False,
            reasoning=reasoning,
            assumptions=assumptions,
            limitations=limitations,
            estimated_resource_impact=impact,
            optimization_score=round(score, 1),
        )

    @classmethod
    def _solve_reserve_preservation(
        cls,
        req: OptimizationRequest,
        teams: List[ResponseTeam],
        resources: List[Resource],
    ) -> Optional[RecommendationOption]:
        """OR-Tools MIP: Preserves local host district reserves by incorporating neighboring mutual-aid units."""
        solver = pywraplp.Solver.CreateSolver("SCIP")
        if not solver or not teams:
            return None

        # Categorize teams: host district vs neighboring/inter-district
        host_district = req.target_district.lower()
        team_data: List[Tuple[ResponseTeam, float, float, bool]] = []

        for t in teams:
            is_local = (t.current_district_name.lower() == host_district)
            dist_km = haversine_distance_meters(req.target_latitude, req.target_longitude, t.latitude, t.longitude) / 1000.0
            eta_mins = cls._calculate_transit_time(dist_km, req.road_access_severed, req.is_coastal_surge)
            team_data.append((t, dist_km, eta_mins, is_local))

        x = [solver.BoolVar(f"team_{i}") for i in range(len(teams))]

        # Objective: Prefer non-local or low-depletion units while bounding distance
        objective = solver.Objective()
        for i, (t, dist_km, eta_mins, is_local) in enumerate(team_data):
            # Penalty for using local team (preserves local reserve), plus transit time
            penalty = (eta_mins * 0.5) + (25.0 if is_local else 0.0)
            objective.SetCoefficient(x[i], penalty)
        objective.SetMinimization()

        # Constraint: Choose 1 unit
        solver.Add(solver.Sum(x) == 1)

        status = solver.Solve()
        if status not in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE):
            return None

        selected_teams = [team_data[i][0] for i in range(len(teams)) if x[i].solution_value() > 0.5]
        if not selected_teams:
            return None

        sel_team = selected_teams[0]
        sel_dist = next(d for t, d, _, _ in team_data if t.id == sel_team.id)
        sel_eta = next(e for t, _, e, _ in team_data if t.id == sel_team.id)

        chosen_resources = resources[:1] if resources else []
        rescue_cap = getattr(sel_team, "rescue_capacity_persons", 30)

        reasoning = (
            f"Optimized for strategic reserve preservation: Dispatches {sel_team.name} from {sel_team.current_district_name} "
            f"to protect the host district's ({req.target_district}) minimum local reserves for potential secondary surges."
        )

        assumptions = [
            "Activates formal ODRN Inter-District Mutual Aid protocol.",
            "Assumes inter-district transport authorization cleared via State Emergency Operations Centre (SEOC).",
            "Calculated transit times assume normal state highway transit without localized roadblock.",
        ]

        limitations = [
            f"Extended transit time ({int(sel_eta)} mins) due to inter-district mobilization.",
            "Requires coordination between two District Emergency Operations Centres (DEOCs).",
        ]

        impact = {
            "target_district": req.target_district,
            "local_station_depletion_percent": 0.0 if sel_team.current_district_name.lower() != host_district else 20.0,
            "estimated_wave_capacity": rescue_cap,
            "estimated_arrival_window_minutes": int(sel_eta),
        }

        score = max(50.0, min(90.0, 85.0 - (sel_eta * 0.3)))

        return RecommendationOption(
            strategy_id="RESERVE_PRESERVATION",
            title="Strategic Sustainability & Mutual Aid",
            recommended_teams=[team_to_view(t) for t in selected_teams],
            recommended_resources=[resource_to_view(r) for r in chosen_resources],
            total_personnel_deployed=sel_team.total_personnel,
            total_rescue_capacity_persons=rescue_cap,
            estimated_distance_km=round(sel_dist, 1),
            estimated_arrival_minutes=sel_eta,
            telemetry_source="CALCULATED_ESTIMATE",
            is_live_telemetry=False,
            reasoning=reasoning,
            assumptions=assumptions,
            limitations=limitations,
            estimated_resource_impact=impact,
            optimization_score=round(score, 1),
        )


response_optimizer = ResponseOptimizationEngine()
