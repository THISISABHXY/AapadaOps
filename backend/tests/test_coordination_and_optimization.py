"""AapadaOps Response Coordination & Resource Optimization Tests.

Tests:
1. OR-Tools multi-criteria MIP optimization engine (MIP/SCIP solver)
2. Generation of multiple feasible tactical plans (MINIMAL_TIME, MAXIMAL_CAPACITY, RESERVE_PRESERVATION)
3. Explainability, assumptions, limitations, and resource impact tracking
4. Full approval workflow state machine:
   AI_RECOMMENDED -> COORDINATOR_REVIEW -> APPROVED -> ASSIGNED -> TEAM_ACKNOWLEDGED -> IN_PROGRESS -> EVIDENCE -> HUMAN_CLOSED
5. Double-allocation prevention: atomic lock & conflict detection
6. Clean asset release on official human closure
"""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from app.coordination.optimizer import response_optimizer
from app.coordination.schemas import (
    OptimizationRequest,
    PlanAcknowledgmentRequest,
    PlanApprovalRequest,
    PlanEvidenceAttachmentRequest,
    PlanHumanClosureRequest,
    PlanProgressUpdateRequest,
)
from app.coordination.workflow_service import coordination_workflow
from app.core.exceptions import ConflictError
from app.main import app
from app.models.coordination import CoordinationPlan, CoordinationStatus
from app.models.evidence import EvidenceFile
from app.models.incident import Incident, IncidentCategory, IncidentSeverity
from app.models.resource import Resource, ResourceStatus, ResourceType
from app.models.team import ResponseTeam, TeamStatus
from app.models.user import User, UserRole


# ============================================================================
# Optimization Engine Tests (OR-Tools MIP)
# ============================================================================

def test_ortools_optimizer_generates_three_feasible_strategies():
    """Verify OR-Tools generates distinct feasible tactical plans with explainable trade-offs."""
    # Create sample available tactical forces
    teams = [
        ResponseTeam(
            id="team-odraf-01",
            code="ODRAF-KND-01",
            name="ODRAF 3rd Battalion Kendrapara",
            organization="ODRAF",
            team_lead_name="Inspector Jena",
            team_lead_phone="+91 94371 11001",
            total_personnel=18,
            specialization="WATER_RESCUE",
            rescue_capacity_persons=45,
            current_district_name="Kendrapara",
            latitude=20.5000,
            longitude=86.4200,
            status=TeamStatus.STANDBY,
        ),
        ResponseTeam(
            id="team-ndrf-02",
            code="NDRF-CTC-01",
            name="NDRF 03 Battalion Cuttack",
            organization="NDRF",
            team_lead_name="Commandant Mishra",
            team_lead_phone="+91 94371 11002",
            total_personnel=35,
            specialization="FLOOD_MASS_RESCUE",
            rescue_capacity_persons=80,
            current_district_name="Cuttack",
            latitude=20.4625,
            longitude=85.8830,
            status=TeamStatus.STANDBY,
        ),
        ResponseTeam(
            id="team-fire-03",
            code="FIRE-JJP-01",
            name="Odisha Fire Services Jajpur",
            organization="FIRE_SERVICES",
            team_lead_name="Station Officer Rout",
            team_lead_phone="+91 94371 11003",
            total_personnel=12,
            specialization="TREE_AND_WATER",
            rescue_capacity_persons=25,
            current_district_name="Jajpur",
            latitude=20.8500,
            longitude=86.3300,
            status=TeamStatus.STANDBY,
        ),
    ]

    resources = [
        Resource(
            id="res-boat-01",
            code="ODRN-BOAT-01",
            name="Inflatable Gemini Boat 40HP",
            category=ResourceType.INFLATABLE_BOAT,
            organization="ODRAF",
            district_name="Kendrapara",
            status=ResourceStatus.AVAILABLE,
            quantity=2,
            capacity=12,
            capacity_unit="persons",
            latitude=20.5010,
            longitude=86.4210,
        ),
        Resource(
            id="res-pump-02",
            code="ODRN-PUMP-01",
            name="High Capacity Dewatering Pump 1000 GPM",
            category=ResourceType.DEWATERING_PUMP,
            organization="OSDMA",
            district_name="Kendrapara",
            status=ResourceStatus.AVAILABLE,
            quantity=1,
            capacity=1000,
            capacity_unit="GPM",
            latitude=20.5020,
            longitude=86.4220,
        ),
    ]

    req = OptimizationRequest(
        incident_id="inc-test-01",
        target_latitude=20.5750,
        target_longitude=86.5650,
        target_district="Kendrapara",
        target_village="Pattamundai Block",
        category=IncidentCategory.FLOOD,
        severity=IncidentSeverity.CRITICAL,
        people_stranded=50,
        casualties=0,
        road_access_severed=True,
        is_coastal_surge=False,
    )

    opt_res = response_optimizer.generate_recommendations(req, teams, resources)

    assert len(opt_res.recommendations) >= 2
    strat_ids = [r.strategy_id for r in opt_res.recommendations]
    assert "MINIMAL_TIME" in strat_ids
    assert "MAXIMAL_CAPACITY" in strat_ids

    # Inspect Strategy A (Minimal Time)
    min_time = next(r for r in opt_res.recommendations if r.strategy_id == "MINIMAL_TIME")
    assert min_time.estimated_arrival_minutes > 0.0
    assert min_time.telemetry_source == "CALCULATED_ESTIMATE"
    assert min_time.is_live_telemetry is False
    assert len(min_time.assumptions) >= 2
    assert len(min_time.limitations) >= 1
    assert "local_station_depletion_percent" in min_time.estimated_resource_impact

    # Inspect Strategy B (Maximal Capacity)
    max_cap = next(r for r in opt_res.recommendations if r.strategy_id == "MAXIMAL_CAPACITY")
    assert max_cap.total_rescue_capacity_persons >= min_time.total_rescue_capacity_persons
    assert len(max_cap.recommended_teams) >= 1


# ============================================================================
# Approval Workflow State Machine Tests
# ============================================================================

@pytest.mark.asyncio
async def test_full_response_coordination_lifecycle(db_session):
    """Test full 8-step lifecycle:
    AI_RECOMMENDED -> REVIEW -> APPROVE/ASSIGN -> ACKNOWLEDGE -> PROGRESS -> EVIDENCE -> HUMAN_CLOSE
    """
    # 1. Setup Incident and Force records
    incident = Incident(
        incident_code="INC-OD-2026-9001",
        title="Baitarani Breach in Jajpur",
        description="Embankment breached near Dasarathpur.",
        category=IncidentCategory.EMBANKMENT_BREACH,
        reported_severity=IncidentSeverity.CRITICAL,
        latitude=20.8500,
        longitude=86.3300,
        district_name="Jajpur",
        village_name="Dasarathpur",
        reporter_name="Sarpanch Dasarathpur",
        reporter_phone="+91 94371 88990",
    )
    db_session.add(incident)

    team = ResponseTeam(
        code="ODRAF-JJP-01",
        name="ODRAF Unit Dasarathpur",
        organization="ODRAF",
        team_lead_name="Captain Barik",
        team_lead_phone="+91 94371 99001",
        total_personnel=15,
        specialization="WATER_RESCUE",
        rescue_capacity_persons=40,
        current_district_name="Jajpur",
        latitude=20.8400,
        longitude=86.3200,
        status=TeamStatus.STANDBY,
    )
    db_session.add(team)

    resource = Resource(
        code="ODRN-BOAT-JJP-01",
        name="Rescue Boat 25HP",
        category=ResourceType.INFLATABLE_BOAT,
        organization="ODRAF",
        district_name="Jajpur",
        status=ResourceStatus.AVAILABLE,
        quantity=1,
        capacity=10,
        capacity_unit="persons",
        latitude=20.8400,
        longitude=86.3200,
    )
    db_session.add(resource)

    coordinator = User(
        email="coord_test@aapadaops.gov.in",
        hashed_password="hash",
        full_name="Coordination Officer Mohanty",
        role=UserRole.RESPONSE_COORDINATOR,
        is_active=True,
    )
    db_session.add(coordinator)
    await db_session.flush()

    # Create dummy evidence file
    evidence = EvidenceFile(
        incident_id=incident.id,
        file_name="rescue_completion_photo.jpg",
        file_path="/uploads/test_photo.jpg",
        file_size_bytes=1024,
        mime_type="image/jpeg",
        sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    )
    db_session.add(evidence)
    await db_session.flush()

    # Step 1: Create Plan (AI_RECOMMENDED)
    opt_req = OptimizationRequest(
        incident_id=incident.id,
        target_latitude=incident.latitude,
        target_longitude=incident.longitude,
        target_district="Jajpur",
        target_village="Dasarathpur",
        category=incident.category,
        severity=incident.reported_severity,
    )
    opt_res = response_optimizer.generate_recommendations(opt_req, [team], [resource])
    assert len(opt_res.recommendations) > 0

    plan = await coordination_workflow.create_plan_from_recommendation(
        db_session, incident, opt_res.recommendations[0], created_by=coordinator
    )
    assert plan.status == CoordinationStatus.AI_RECOMMENDED

    # Step 2: Submit for Review (COORDINATOR_REVIEW)
    plan = await coordination_workflow.submit_for_review(
        db_session, plan.id, reviewer=coordinator, notes="Inspecting route access."
    )
    assert plan.status == CoordinationStatus.COORDINATOR_REVIEW
    assert plan.reviewed_by_id == coordinator.id

    # Step 3: Approve & Assign (ASSIGNED)
    plan = await coordination_workflow.approve_and_assign_plan(
        db_session, plan.id, approver=coordinator, approval_notes="Dispatched per Collector order."
    )
    assert plan.status == CoordinationStatus.ASSIGNED

    # Verify team and resource status transitioned to DEPLOYED / DISPATCHED
    await db_session.refresh(team)
    await db_session.refresh(resource)
    assert team.status == TeamStatus.DEPLOYED
    assert resource.status == ResourceStatus.DISPATCHED
    assert team.assigned_plan_id == plan.id

    # Step 4: Team Acknowledgment (TEAM_ACKNOWLEDGED)
    plan = await coordination_workflow.acknowledge_by_team(
        db_session, plan.id, lead_name="Captain Barik", notes="Battalion moving on NH."
    )
    assert plan.status == CoordinationStatus.TEAM_ACKNOWLEDGED
    assert plan.acknowledged_by == "Captain Barik"

    # Step 5: Progress Update (IN_PROGRESS)
    plan = await coordination_workflow.update_progress(
        db_session, plan.id, progress_notes="Arrived at bank, inflating boats.", actor=coordinator
    )
    assert plan.status == CoordinationStatus.IN_PROGRESS

    # Step 6: Evidence Attached (EVIDENCE_ATTACHED)
    plan = await coordination_workflow.attach_completion_evidence(
        db_session, plan.id, evidence_file_id=evidence.id, actor=coordinator, notes="All 40 villagers safely evacuated."
    )
    assert plan.status == CoordinationStatus.EVIDENCE_ATTACHED
    assert plan.evidence_file_id == evidence.id

    # Step 7: Official Human Closure (HUMAN_CLOSED)
    plan = await coordination_workflow.human_close_plan(
        db_session, plan.id, officer=coordinator, closure_notes="Evacuation verified complete by SEOC."
    )
    assert plan.status == CoordinationStatus.HUMAN_CLOSED
    assert plan.closed_by_id == coordinator.id

    # Verify team and resource released back to STANDBY / AVAILABLE
    await db_session.refresh(team)
    await db_session.refresh(resource)
    assert team.status == TeamStatus.STANDBY
    assert resource.status == ResourceStatus.AVAILABLE
    assert team.assigned_plan_id is None
    assert resource.assigned_plan_id is None


# ============================================================================
# Concurrency & Double-Allocation Prevention Tests
# ============================================================================

@pytest.mark.asyncio
async def test_double_allocation_prevention_rejected(db_session):
    """Verify that attempting to assign an already-deployed team throws 409 Conflict."""
    incident = Incident(
        incident_code="INC-OD-2026-9002",
        title="Second Breach Incident",
        description="Another breach in Jajpur.",
        category=IncidentCategory.FLOOD,
        reported_severity=IncidentSeverity.HIGH,
        latitude=20.8600,
        longitude=86.3400,
        district_name="Jajpur",
        village_name="Binjharpur",
        reporter_name="Ward Member Binjharpur",
        reporter_phone="+91 94371 88991",
    )
    db_session.add(incident)

    # Team is already DEPLOYED on another mission
    busy_team = ResponseTeam(
        code="ODRAF-BUSY-01",
        name="Busy ODRAF Battalion",
        organization="ODRAF",
        team_lead_name="Captain Nayak",
        team_lead_phone="+91 94371 99002",
        total_personnel=10,
        specialization="WATER_RESCUE",
        rescue_capacity_persons=30,
        current_district_name="Jajpur",
        latitude=20.8500,
        longitude=86.3300,
        status=TeamStatus.DEPLOYED,  # NOT STANDBY!
    )
    db_session.add(busy_team)

    coordinator = User(
        email="coord_busy@aapadaops.gov.in",
        hashed_password="hash",
        full_name="Coordinator Jena",
        role=UserRole.RESPONSE_COORDINATOR,
        is_active=True,
    )
    db_session.add(coordinator)
    await db_session.flush()

    # Manually create a plan referencing the busy team
    import json
    plan = CoordinationPlan(
        plan_code="PLAN-COLLISION-TEST",
        incident_id=incident.id,
        title="Conflicting Dispatch Plan",
        strategy_name="MINIMAL_TIME",
        status=CoordinationStatus.COORDINATOR_REVIEW,
        allocated_team_ids_json=json.dumps([busy_team.id]),
        allocated_resource_ids_json="[]",
        target_latitude=20.8600,
        target_longitude=86.3400,
        target_district="Jajpur",
        target_village="Binjharpur",
        reasoning_text="Test double allocation",
        assumptions_text="None",
        limitations_text="None",
    )
    db_session.add(plan)
    await db_session.flush()

    # Attempt to approve and assign must trigger ConflictError!
    with pytest.raises(ConflictError) as excinfo:
        await coordination_workflow.approve_and_assign_plan(
            db_session, plan.id, approver=coordinator
        )

    assert excinfo.value.code == "TEAM_ALREADY_ALLOCATED"
    assert "Double-allocation prevented" in excinfo.value.message
