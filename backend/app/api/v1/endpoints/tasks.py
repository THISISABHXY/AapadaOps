"""AapadaOps Operational Task Dispatch & Kanban Management API."""

import random
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.core.websocket_manager import ws_manager
from app.api.v1.deps import require_roles
from app.models.incident import Incident, IncidentStatus
from app.models.task import Task, TaskStatus
from app.models.team import ResponseTeam, TeamStatus
from app.models.user import User, UserRole
from app.schemas.resource import TaskCreate, TaskResponse, TaskUpdate
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/tasks", tags=["Tactical Tasks"])


@router.get("", response_model=List[TaskResponse])
async def list_tasks(
    incident_id: Optional[str] = None,
    team_id: Optional[str] = None,
    status: Optional[TaskStatus] = None,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve tactical mission tasks across operational Kanban columns."""
    query = select(Task)
    if incident_id:
        query = query.where(Task.incident_id == incident_id)
    if team_id:
        query = query.where(Task.assigned_team_id == team_id)
    if status:
        query = query.where(Task.status == status)

    query = query.order_by(Task.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def dispatch_task(
    task_in: TaskCreate,
    current_user: User = Depends(
        require_roles(
            UserRole.SUPER_ADMIN,
            UserRole.DISTRICT_COLLECTOR,
            UserRole.RESPONSE_COORDINATOR,
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    """Dispatch tactical force to incident location with SLA deadline."""
    # Verify Incident exists
    inc_res = await db.execute(select(Incident).where(Incident.id == task_in.incident_id))
    incident = inc_res.scalar_one_or_none()
    if not incident:
        raise NotFoundError("Incident", task_in.incident_id)

    # Calculate SLA deadline
    deadline = datetime.now(timezone.utc) + timedelta(hours=task_in.sla_hours)
    task_code = f"TSK-{task_in.priority[:3]}-{random.randint(1000, 9999)}"

    task = Task(
        task_code=task_code,
        incident_id=incident.id,
        assigned_team_id=task_in.assigned_team_id,
        title=task_in.title,
        description=task_in.description,
        priority=task_in.priority,
        sla_hours=task_in.sla_hours,
        deadline=deadline,
        status=TaskStatus.PENDING,
        target_village=task_in.target_village,
        target_latitude=task_in.target_latitude,
        target_longitude=task_in.target_longitude,
        dispatch_notes=task_in.dispatch_notes,
        created_by_id=current_user.id,
    )
    db.add(task)
    await db.flush()

    # Update team status to DEPLOYED if assigned
    if task_in.assigned_team_id:
        t_res = await db.execute(
            select(ResponseTeam).where(ResponseTeam.id == task_in.assigned_team_id)
        )
        team = t_res.scalar_one_or_none()
        if team:
            team.status = TeamStatus.DEPLOYED

    # Update incident status to ASSIGNED if verified
    if incident.status in (IncidentStatus.VERIFIED, IncidentStatus.PRIORITIZED):
        incident.status = IncidentStatus.ASSIGNED

    await log_audit_event(
        db,
        action="DISPATCH_TASK",
        entity_type="TASK",
        entity_id=task.id,
        actor=current_user,
        description=f"Dispatched task {task.task_code} for incident {incident.incident_code} (SLA: {task.sla_hours}h).",
    )

    await db.commit()
    await db.refresh(task)

    # Real-time WebSocket broadcast
    await ws_manager.broadcast(
        channel="tasks",
        message={
            "event": "TASK_DISPATCHED",
            "task_id": task.id,
            "task_code": task.task_code,
            "incident_id": task.incident_id,
            "priority": task.priority,
            "target_village": task.target_village,
            "sla_hours": task.sla_hours,
        },
    )

    return task


@router.patch("/{task_id}", response_model=TaskResponse)
@router.patch("/{task_id}/status", response_model=TaskResponse)
async def update_task_status(
    task_id: str,
    update_in: TaskUpdate,
    current_user: User = Depends(
        require_roles(
            UserRole.SUPER_ADMIN,
            UserRole.DISTRICT_COLLECTOR,
            UserRole.RESPONSE_COORDINATOR,
            UserRole.FIELD_WORKER,
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    """Transition task status across Kanban columns (PENDING -> IN_PROGRESS -> COMPLETED)."""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise NotFoundError("Task", task_id)

    previous_status = task.status
    if update_in.status:
        task.status = update_in.status
    if update_in.resolution_notes:
        task.resolution_notes = update_in.resolution_notes

    if update_in.status == TaskStatus.COMPLETED:
        task.completed_at = datetime.now(timezone.utc)
        # Release assigned team back to STANDBY
        if task.assigned_team_id:
            t_res = await db.execute(
                select(ResponseTeam).where(ResponseTeam.id == task.assigned_team_id)
            )
            team = t_res.scalar_one_or_none()
            if team:
                team.status = TeamStatus.STANDBY

    await log_audit_event(
        db,
        action="UPDATE_TASK_STATUS",
        entity_type="TASK",
        entity_id=task.id,
        actor=current_user,
        description=f"Task {task.task_code} changed from {previous_status.value} to {task.status.value}.",
        changes={"status": task.status.value, "notes": update_in.resolution_notes},
    )

    await db.commit()
    await db.refresh(task)

    # Real-time WebSocket broadcast
    await ws_manager.broadcast(
        channel="tasks",
        message={
            "event": "TASK_STATUS_UPDATED",
            "task_id": task.id,
            "previous_status": previous_status.value,
            "new_status": task.status.value,
            "updated_at": task.updated_at.isoformat(),
        },
    )

    return task
