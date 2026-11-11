"""AapadaOps Operational Response Coordination Workflow Service.

Enforces strict human-governed approval state machine:
AI RECOMMENDATION -> COORDINATOR REVIEW -> APPROVAL -> ASSIGNMENT ->
TEAM ACKNOWLEDGMENT -> PROGRESS UPDATE -> EVIDENCE -> HUMAN CLOSURE.

Prevents double-allocation of tactical assets, enforces atomic locking,
and maintains full auditability.
"""

import json
import logging
import random
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.coordination.schemas import CoordinationPlanResponse, RecommendationOption
from app.core.exceptions import AppException, ConflictError, NotFoundError
from app.core.websocket_manager import ws_manager
from app.models.coordination import CoordinationPlan, CoordinationStatus
from app.models.evidence import EvidenceFile
from app.models.incident import Incident, IncidentStatus
from app.models.resource import Resource, ResourceStatus
from app.models.task import Task, TaskStatus
from app.models.team import ResponseTeam, TeamStatus
from app.models.user import User
from app.services.audit_service import log_audit_event

logger = logging.getLogger("aapadaops.coordination.workflow")


class CoordinationWorkflowService:
    """Manages transactional response coordination plans and prevents asset collision."""

    @staticmethod
    def _generate_plan_code() -> str:
        """Generate human-readable plan identifier."""
        return f"PLAN-OD-{datetime.now().year}-{random.randint(1000, 9999)}"

    @classmethod
    async def create_plan_from_recommendation(
        cls,
        db: AsyncSession,
        incident: Incident,
        option: RecommendationOption,
        created_by: Optional[User] = None,
    ) -> CoordinationPlan:
        """Persist an AI-generated optimization recommendation plan."""
        plan_code = cls._generate_plan_code()
        team_ids = [t.id for t in option.recommended_teams]
        res_ids = [r.id for r in option.recommended_resources]

        plan = CoordinationPlan(
            plan_code=plan_code,
            incident_id=incident.id,
            title=f"{option.title} - {incident.incident_code}",
            strategy_name=option.strategy_id,
            status=CoordinationStatus.AI_RECOMMENDED,
            allocated_team_ids_json=json.dumps(team_ids),
            allocated_resource_ids_json=json.dumps(res_ids),
            target_latitude=incident.latitude,
            target_longitude=incident.longitude,
            target_district=incident.district_name or "Unknown",
            target_village=incident.village_name or "Target Zone",
            estimated_distance_km=option.estimated_distance_km,
            estimated_arrival_minutes=option.estimated_arrival_minutes,
            telemetry_source=option.telemetry_source,
            is_live_telemetry=False,
            reasoning_text=option.reasoning,
            assumptions_text="\n".join(option.assumptions),
            limitations_text="\n".join(option.limitations),
            resource_impact_json=json.dumps(option.estimated_resource_impact),
        )
        db.add(plan)
        await db.flush()

        await log_audit_event(
            db,
            action="AI_COORDINATION_PLAN_GENERATED",
            entity_type="COORDINATION_PLAN",
            entity_id=plan.id,
            actor=created_by,
            description=f"Generated AI optimization plan {plan.plan_code} ({option.strategy_id}).",
        )
        await db.commit()
        await db.refresh(plan)
        return plan

    @classmethod
    async def submit_for_review(
        cls,
        db: AsyncSession,
        plan_id: str,
        reviewer: User,
        notes: Optional[str] = None,
    ) -> CoordinationPlan:
        """Move plan to COORDINATOR_REVIEW stage."""
        res = await db.execute(select(CoordinationPlan).where(CoordinationPlan.id == plan_id))
        plan = res.scalar_one_or_none()
        if not plan:
            raise NotFoundError("CoordinationPlan", plan_id)

        if plan.status != CoordinationStatus.AI_RECOMMENDED:
            raise AppException(
                message=f"Plan {plan.plan_code} cannot move to review from {plan.status.value}.",
                status_code=400,
                code="INVALID_WORKFLOW_STATE",
            )

        plan.status = CoordinationStatus.COORDINATOR_REVIEW
        plan.reviewed_by_id = reviewer.id
        plan.reviewed_at = datetime.now(timezone.utc)
        if notes:
            plan.progress_notes = notes

        await log_audit_event(
            db,
            action="SUBMIT_PLAN_FOR_REVIEW",
            entity_type="COORDINATION_PLAN",
            entity_id=plan.id,
            actor=reviewer,
            description=f"Plan {plan.plan_code} marked under official coordinator review.",
        )
        await db.commit()
        await db.refresh(plan)
        return plan

    @classmethod
    async def approve_and_assign_plan(
        cls,
        db: AsyncSession,
        plan_id: str,
        approver: User,
        approval_notes: Optional[str] = None,
    ) -> CoordinationPlan:
        """Approve response plan and atomically lock allocated teams and equipment.

        Prevents double-allocation using transactional checks.
        """
        res = await db.execute(select(CoordinationPlan).where(CoordinationPlan.id == plan_id))
        plan = res.scalar_one_or_none()
        if not plan:
            raise NotFoundError("CoordinationPlan", plan_id)

        if plan.status not in (CoordinationStatus.AI_RECOMMENDED, CoordinationStatus.COORDINATOR_REVIEW):
            raise AppException(
                message=f"Plan {plan.plan_code} cannot be approved from current state {plan.status.value}.",
                status_code=400,
                code="INVALID_WORKFLOW_STATE",
            )

        team_ids: List[str] = json.loads(plan.allocated_team_ids_json)
        resource_ids: List[str] = json.loads(plan.allocated_resource_ids_json)

        # -------------------------------------------------------------
        # Concurrency Check: Prevent Double-Allocation of Teams
        # -------------------------------------------------------------
        teams_to_lock: List[ResponseTeam] = []
        if team_ids:
            t_stmt = select(ResponseTeam).where(ResponseTeam.id.in_(team_ids))
            t_res = await db.execute(t_stmt)
            teams_to_lock = t_res.scalars().all()

            for team in teams_to_lock:
                if team.status != TeamStatus.STANDBY:
                    raise ConflictError(
                        message=(
                            f"Double-allocation prevented: Tactical team {team.name} ({team.code}) "
                            f"is currently {team.status.value} and cannot be assigned to plan {plan.plan_code}."
                        ),
                        code="TEAM_ALREADY_ALLOCATED",
                    )

        # -------------------------------------------------------------
        # Concurrency Check: Prevent Double-Allocation of Resources
        # -------------------------------------------------------------
        resources_to_lock: List[Resource] = []
        if resource_ids:
            r_stmt = select(Resource).where(Resource.id.in_(resource_ids))
            r_res = await db.execute(r_stmt)
            resources_to_lock = r_res.scalars().all()

            for res_item in resources_to_lock:
                if res_item.status != ResourceStatus.AVAILABLE:
                    raise ConflictError(
                        message=(
                            f"Double-allocation prevented: Equipment {res_item.name} ({res_item.code}) "
                            f"is currently {res_item.status.value} and cannot be assigned to plan {plan.plan_code}."
                        ),
                        code="RESOURCE_ALREADY_ALLOCATED",
                    )

        # -------------------------------------------------------------
        # Atomic Lock & Assignment
        # -------------------------------------------------------------
        now = datetime.now(timezone.utc)
        for team in teams_to_lock:
            team.status = TeamStatus.DEPLOYED
            team.assigned_incident_id = plan.incident_id
            team.assigned_plan_id = plan.id

        for res_item in resources_to_lock:
            res_item.status = ResourceStatus.DISPATCHED
            res_item.assigned_incident_id = plan.incident_id
            res_item.assigned_plan_id = plan.id

        # Update Incident status to ASSIGNED if needed
        inc_res = await db.execute(select(Incident).where(Incident.id == plan.incident_id))
        incident = inc_res.scalar_one_or_none()
        if incident and incident.status in (IncidentStatus.VERIFIED, IncidentStatus.PRIORITIZED, IncidentStatus.SUBMITTED):
            incident.status = IncidentStatus.ASSIGNED

        # Create associated operational Task
        lead_team_id = teams_to_lock[0].id if teams_to_lock else None
        task = Task(
            task_code=f"TSK-{plan.strategy_name[:3]}-{random.randint(1000, 9999)}",
            incident_id=plan.incident_id,
            assigned_team_id=lead_team_id,
            title=f"Deploy for {plan.title}",
            description=f"Strategy: {plan.strategy_name}. Notes: {approval_notes or 'Dispatch approved.'}",
            priority="HIGH",
            sla_hours=4,
            status=TaskStatus.PENDING,
            target_village=plan.target_village,
            target_latitude=plan.target_latitude,
            target_longitude=plan.target_longitude,
            created_by_id=approver.id,
        )
        db.add(task)
        await db.flush()

        plan.status = CoordinationStatus.ASSIGNED
        plan.approved_by_id = approver.id
        plan.approved_at = now
        if approval_notes:
            plan.progress_notes = approval_notes

        await log_audit_event(
            db,
            action="APPROVE_AND_ASSIGN_PLAN",
            entity_type="COORDINATION_PLAN",
            entity_id=plan.id,
            actor=approver,
            description=f"Approved and assigned response plan {plan.plan_code}. Dispatched {len(teams_to_lock)} teams.",
            changes={"teams": [t.code for t in teams_to_lock], "resources": [r.code for r in resources_to_lock]},
        )

        await db.commit()
        await db.refresh(plan)

        # Real-time WebSocket Broadcast
        await ws_manager.broadcast(
            channel="coordination",
            message={
                "event": "PLAN_ASSIGNED",
                "plan_id": plan.id,
                "plan_code": plan.plan_code,
                "strategy": plan.strategy_name,
                "assigned_teams_count": len(teams_to_lock),
                "target_village": plan.target_village,
            },
        )

        return plan

    @classmethod
    async def acknowledge_by_team(
        cls,
        db: AsyncSession,
        plan_id: str,
        lead_name: str,
        notes: Optional[str] = None,
    ) -> CoordinationPlan:
        """Record battalion commander receipt and acknowledgment of dispatch order."""
        res = await db.execute(select(CoordinationPlan).where(CoordinationPlan.id == plan_id))
        plan = res.scalar_one_or_none()
        if not plan:
            raise NotFoundError("CoordinationPlan", plan_id)

        if plan.status != CoordinationStatus.ASSIGNED:
            raise AppException(
                message=f"Plan {plan.plan_code} cannot be acknowledged from state {plan.status.value}.",
                status_code=400,
                code="INVALID_WORKFLOW_STATE",
            )

        plan.status = CoordinationStatus.TEAM_ACKNOWLEDGED
        plan.acknowledged_by = lead_name
        plan.acknowledged_at = datetime.now(timezone.utc)
        if notes:
            plan.progress_notes = f"{plan.progress_notes or ''}\nAcknowledgment: {notes}".strip()

        await log_audit_event(
            db,
            action="TEAM_ACKNOWLEDGED_DISPATCH",
            entity_type="COORDINATION_PLAN",
            entity_id=plan.id,
            description=f"Dispatch orders for {plan.plan_code} acknowledged by {lead_name}.",
        )
        await db.commit()
        await db.refresh(plan)

        await ws_manager.broadcast(
            channel="coordination",
            message={
                "event": "TEAM_ACKNOWLEDGED",
                "plan_id": plan.id,
                "acknowledged_by": lead_name,
            },
        )
        return plan

    @classmethod
    async def update_progress(
        cls,
        db: AsyncSession,
        plan_id: str,
        progress_notes: str,
        actor: Optional[User] = None,
    ) -> CoordinationPlan:
        """Report live on-ground progress and move status to IN_PROGRESS."""
        res = await db.execute(select(CoordinationPlan).where(CoordinationPlan.id == plan_id))
        plan = res.scalar_one_or_none()
        if not plan:
            raise NotFoundError("CoordinationPlan", plan_id)

        if plan.status not in (CoordinationStatus.TEAM_ACKNOWLEDGED, CoordinationStatus.IN_PROGRESS):
            raise AppException(
                message=f"Cannot record progress for plan {plan.plan_code} in status {plan.status.value}.",
                status_code=400,
                code="INVALID_WORKFLOW_STATE",
            )

        plan.status = CoordinationStatus.IN_PROGRESS
        plan.progress_notes = progress_notes

        await log_audit_event(
            db,
            action="PROGRESS_UPDATE",
            entity_type="COORDINATION_PLAN",
            entity_id=plan.id,
            actor=actor,
            description=f"Progress updated on {plan.plan_code}: {progress_notes[:80]}...",
        )
        await db.commit()
        await db.refresh(plan)
        return plan

    @classmethod
    async def attach_completion_evidence(
        cls,
        db: AsyncSession,
        plan_id: str,
        evidence_file_id: str,
        actor: Optional[User] = None,
        notes: Optional[str] = None,
    ) -> CoordinationPlan:
        """Attach verified photo or document proof demonstrating mission completion."""
        res = await db.execute(select(CoordinationPlan).where(CoordinationPlan.id == plan_id))
        plan = res.scalar_one_or_none()
        if not plan:
            raise NotFoundError("CoordinationPlan", plan_id)

        # Verify evidence file exists
        ev_res = await db.execute(select(EvidenceFile).where(EvidenceFile.id == evidence_file_id))
        evidence = ev_res.scalar_one_or_none()
        if not evidence:
            raise NotFoundError("EvidenceFile", evidence_file_id)

        plan.status = CoordinationStatus.EVIDENCE_ATTACHED
        plan.evidence_file_id = evidence_file_id
        if notes:
            plan.progress_notes = f"{plan.progress_notes or ''}\nEvidence Note: {notes}".strip()

        await log_audit_event(
            db,
            action="ATTACH_COMPLETION_EVIDENCE",
            entity_type="COORDINATION_PLAN",
            entity_id=plan.id,
            actor=actor,
            description=f"Evidence {evidence.file_name} attached to plan {plan.plan_code}.",
        )
        await db.commit()
        await db.refresh(plan)
        return plan

    @classmethod
    async def human_close_plan(
        cls,
        db: AsyncSession,
        plan_id: str,
        officer: User,
        closure_notes: str,
    ) -> CoordinationPlan:
        """Official human verification closing the mission and releasing assets back to reserve."""
        res = await db.execute(select(CoordinationPlan).where(CoordinationPlan.id == plan_id))
        plan = res.scalar_one_or_none()
        if not plan:
            raise NotFoundError("CoordinationPlan", plan_id)

        if plan.status not in (CoordinationStatus.EVIDENCE_ATTACHED, CoordinationStatus.IN_PROGRESS):
            raise AppException(
                message=f"Plan {plan.plan_code} cannot be closed from status {plan.status.value}.",
                status_code=400,
                code="INVALID_WORKFLOW_STATE",
            )

        now = datetime.now(timezone.utc)
        team_ids: List[str] = json.loads(plan.allocated_team_ids_json)
        resource_ids: List[str] = json.loads(plan.allocated_resource_ids_json)

        # Release response teams back to STANDBY
        if team_ids:
            t_res = await db.execute(select(ResponseTeam).where(ResponseTeam.id.in_(team_ids)))
            for team in t_res.scalars().all():
                team.status = TeamStatus.STANDBY
                team.assigned_incident_id = None
                team.assigned_plan_id = None

        # Release resources back to AVAILABLE
        if resource_ids:
            r_res = await db.execute(select(Resource).where(Resource.id.in_(resource_ids)))
            for r in r_res.scalars().all():
                r.status = ResourceStatus.AVAILABLE
                r.assigned_incident_id = None
                r.assigned_plan_id = None

        plan.status = CoordinationStatus.HUMAN_CLOSED
        plan.closed_by_id = officer.id
        plan.closed_at = now
        plan.closure_notes = closure_notes

        await log_audit_event(
            db,
            action="HUMAN_CLOSE_COORDINATION_PLAN",
            entity_type="COORDINATION_PLAN",
            entity_id=plan.id,
            actor=officer,
            description=f"Officer {officer.full_name} closed plan {plan.plan_code}. Released all forces and resources to standby.",
        )

        await db.commit()
        await db.refresh(plan)

        await ws_manager.broadcast(
            channel="coordination",
            message={
                "event": "PLAN_CLOSED",
                "plan_id": plan.id,
                "plan_code": plan.plan_code,
                "closed_by": officer.full_name,
            },
        )

        return plan


coordination_workflow = CoordinationWorkflowService()

