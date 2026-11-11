"""AapadaOps Response Coordination and Resource Optimization API Endpoints."""

import json
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.deps import PaginationParams, get_current_user, require_roles
from app.coordination.optimizer import response_optimizer
from app.coordination.schemas import (
    CoordinationPlanResponse,
    OptimizationRequest,
    OptimizationResponse,
    PlanAcknowledgmentRequest,
    PlanApprovalRequest,
    PlanEvidenceAttachmentRequest,
    PlanHumanClosureRequest,
    PlanProgressUpdateRequest,
)
from app.coordination.workflow_service import coordination_workflow
from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.models.coordination import CoordinationPlan, CoordinationStatus
from app.models.incident import Incident
from app.models.resource import Resource, ResourceStatus
from app.models.team import ResponseTeam, TeamStatus
from app.models.user import User, UserRole

router = APIRouter(prefix="/coordination", tags=["Response Coordination & Optimization"])


def _to_plan_response(plan: CoordinationPlan) -> CoordinationPlanResponse:
    """Helper to convert model to response schema with JSON list decoding."""
    team_ids = json.loads(plan.allocated_team_ids_json) if plan.allocated_team_ids_json else []
    res_ids = json.loads(plan.allocated_resource_ids_json) if plan.allocated_resource_ids_json else []
    impact = json.loads(plan.resource_impact_json) if plan.resource_impact_json else {}

    return CoordinationPlanResponse(
        id=plan.id,
        plan_code=plan.plan_code,
        incident_id=plan.incident_id,
        title=plan.title,
        strategy_name=plan.strategy_name,
        status=plan.status,
        allocated_team_ids=team_ids,
        allocated_resource_ids=res_ids,
        target_latitude=plan.target_latitude,
        target_longitude=plan.target_longitude,
        target_district=plan.target_district,
        target_village=plan.target_village,
        estimated_distance_km=plan.estimated_distance_km,
        estimated_arrival_minutes=plan.estimated_arrival_minutes,
        telemetry_source=plan.telemetry_source,
        is_live_telemetry=plan.is_live_telemetry,
        reasoning_text=plan.reasoning_text,
        assumptions_text=plan.assumptions_text,
        limitations_text=plan.limitations_text,
        resource_impact=impact,
        reviewed_by_id=plan.reviewed_by_id,
        reviewed_at=plan.reviewed_at,
        approved_by_id=plan.approved_by_id,
        approved_at=plan.approved_at,
        acknowledged_by=plan.acknowledged_by,
        acknowledged_at=plan.acknowledged_at,
        progress_notes=plan.progress_notes,
        evidence_file_id=plan.evidence_file_id,
        closed_by_id=plan.closed_by_id,
        closed_at=plan.closed_at,
        closure_notes=plan.closure_notes,
        created_at=plan.created_at,
        updated_at=plan.updated_at,
    )


@router.post("/optimize", response_model=OptimizationResponse)
async def generate_response_recommendations(
    request: OptimizationRequest,
    current_user: User = Depends(
        require_roles(
            UserRole.SUPER_ADMIN,
            UserRole.DISTRICT_COLLECTOR,
            UserRole.RESPONSE_COORDINATOR,
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    """Run Google OR-Tools optimization engine to generate feasible tactical options.
    Evaluates team capabilities, travel distance, capacity matching, and reserve impacts.
    """
    # Fetch available standby teams
    t_res = await db.execute(select(ResponseTeam).where(ResponseTeam.status == TeamStatus.STANDBY))
    available_teams = t_res.scalars().all()

    # Fetch available equipment
    r_res = await db.execute(select(Resource).where(Resource.status == ResourceStatus.AVAILABLE))
    available_resources = r_res.scalars().all()

    return response_optimizer.generate_recommendations(
        req=request,
        available_teams=available_teams,
        available_resources=available_resources,
    )


@router.post("/plans/from-recommendation", response_model=CoordinationPlanResponse, status_code=status.HTTP_201_CREATED)
async def save_recommendation_as_plan(
    incident_id: str,
    strategy_id: str,
    current_user: User = Depends(
        require_roles(
            UserRole.SUPER_ADMIN,
            UserRole.DISTRICT_COLLECTOR,
            UserRole.RESPONSE_COORDINATOR,
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    """Persist an optimization option into the database as an AI_RECOMMENDED plan."""
    inc_res = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = inc_res.scalar_one_or_none()
    if not incident:
        raise NotFoundError("Incident", incident_id)

    # Re-run optimization to grab the specific strategy
    t_res = await db.execute(select(ResponseTeam).where(ResponseTeam.status == TeamStatus.STANDBY))
    available_teams = t_res.scalars().all()
    r_res = await db.execute(select(Resource).where(Resource.status == ResourceStatus.AVAILABLE))
    available_resources = r_res.scalars().all()

    opt_req = OptimizationRequest(
        incident_id=incident.id,
        target_latitude=incident.latitude,
        target_longitude=incident.longitude,
        target_district=incident.district_name or "Unknown",
        target_village=incident.village_name or "Target Zone",
        category=incident.category,
        severity=incident.verified_priority or incident.reported_severity,
        people_stranded=incident.stranded_count,
        casualties=incident.casualties_reported,
    )

    opt_res = response_optimizer.generate_recommendations(opt_req, available_teams, available_resources)
    matched_option = next((o for o in opt_res.recommendations if o.strategy_id == strategy_id), None)
    if not matched_option:
        if opt_res.recommendations:
            matched_option = opt_res.recommendations[0]
        else:
            raise NotFoundError("RecommendationStrategy", strategy_id)

    plan = await coordination_workflow.create_plan_from_recommendation(
        db, incident, matched_option, created_by=current_user
    )
    return _to_plan_response(plan)


@router.get("/plans", response_model=List[CoordinationPlanResponse])
async def list_coordination_plans(
    incident_id: Optional[str] = None,
    status_filter: Optional[CoordinationStatus] = None,
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List operational response plans with filtering."""
    stmt = select(CoordinationPlan).order_by(CoordinationPlan.created_at.desc())
    if incident_id:
        stmt = stmt.where(CoordinationPlan.incident_id == incident_id)
    if status_filter:
        stmt = stmt.where(CoordinationPlan.status == status_filter)

    stmt = stmt.offset(pagination.offset).limit(pagination.limit)
    res = await db.execute(stmt)
    plans = res.scalars().all()
    return [_to_plan_response(p) for p in plans]


@router.get("/plans/{plan_id}", response_model=CoordinationPlanResponse)
async def get_coordination_plan(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve coordination plan details."""
    res = await db.execute(select(CoordinationPlan).where(CoordinationPlan.id == plan_id))
    plan = res.scalar_one_or_none()
    if not plan:
        raise NotFoundError("CoordinationPlan", plan_id)
    return _to_plan_response(plan)


@router.post("/plans/{plan_id}/review", response_model=CoordinationPlanResponse)
async def submit_for_review(
    plan_id: str,
    notes: Optional[str] = None,
    current_user: User = Depends(
        require_roles(
            UserRole.SUPER_ADMIN,
            UserRole.DISTRICT_COLLECTOR,
            UserRole.RESPONSE_COORDINATOR,
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    """Move plan to COORDINATOR_REVIEW stage."""
    plan = await coordination_workflow.submit_for_review(db, plan_id, current_user, notes)
    return _to_plan_response(plan)


@router.post("/plans/{plan_id}/approve", response_model=CoordinationPlanResponse)
async def approve_and_assign_plan(
    plan_id: str,
    req: PlanApprovalRequest,
    current_user: User = Depends(
        require_roles(
            UserRole.SUPER_ADMIN,
            UserRole.DISTRICT_COLLECTOR,
            UserRole.RESPONSE_COORDINATOR,
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    """Approve response plan and atomically lock allocated teams and equipment.
    Prevents double-allocation with transactional verification.
    """
    plan = await coordination_workflow.approve_and_assign_plan(db, plan_id, current_user, req.approval_notes)
    return _to_plan_response(plan)


@router.post("/plans/{plan_id}/acknowledge", response_model=CoordinationPlanResponse)
async def acknowledge_dispatch_orders(
    plan_id: str,
    req: PlanAcknowledgmentRequest,
    current_user: User = Depends(
        require_roles(
            UserRole.SUPER_ADMIN,
            UserRole.RESPONSE_COORDINATOR,
            UserRole.FIELD_WORKER,
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    """Team lead acknowledges receipt of tactical dispatch orders."""
    plan = await coordination_workflow.acknowledge_by_team(
        db, plan_id, req.acknowledged_by_lead_name, req.acknowledgment_notes
    )
    return _to_plan_response(plan)


@router.post("/plans/{plan_id}/progress", response_model=CoordinationPlanResponse)
async def update_operational_progress(
    plan_id: str,
    req: PlanProgressUpdateRequest,
    current_user: User = Depends(
        require_roles(
            UserRole.SUPER_ADMIN,
            UserRole.RESPONSE_COORDINATOR,
            UserRole.FIELD_WORKER,
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    """Record on-ground operational progress."""
    plan = await coordination_workflow.update_progress(db, plan_id, req.progress_notes, current_user)
    return _to_plan_response(plan)


@router.post("/plans/{plan_id}/evidence", response_model=CoordinationPlanResponse)
async def attach_completion_evidence(
    plan_id: str,
    req: PlanEvidenceAttachmentRequest,
    current_user: User = Depends(
        require_roles(
            UserRole.SUPER_ADMIN,
            UserRole.RESPONSE_COORDINATOR,
            UserRole.FIELD_WORKER,
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    """Attach photographic or document proof verifying task completion."""
    plan = await coordination_workflow.attach_completion_evidence(
        db, plan_id, req.evidence_file_id, current_user, req.evidence_notes
    )
    return _to_plan_response(plan)


@router.post("/plans/{plan_id}/close", response_model=CoordinationPlanResponse)
async def human_close_plan(
    plan_id: str,
    req: PlanHumanClosureRequest,
    current_user: User = Depends(
        require_roles(
            UserRole.SUPER_ADMIN,
            UserRole.DISTRICT_COLLECTOR,
            UserRole.RESPONSE_COORDINATOR,
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    """Official human closure verifying completion and releasing all tactical assets back to standby."""
    plan = await coordination_workflow.human_close_plan(db, plan_id, current_user, req.closure_notes)
    return _to_plan_response(plan)

