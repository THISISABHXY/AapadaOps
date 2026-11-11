"""AapadaOps API v1 Central Router."""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    ai,
    alerts,
    analytics,
    audit_logs,
    auth,
    coordination,
    districts,
    duplicates,
    evidence,
    incidents,
    reports,
    resources,
    shelters,
    tasks,
    teams,
    users,
    verification,
    websockets,
)

api_router = APIRouter()

# Register endpoint routers
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(districts.router)
api_router.include_router(incidents.router)
api_router.include_router(reports.router)
api_router.include_router(evidence.router)
api_router.include_router(duplicates.router)
api_router.include_router(verification.router)
api_router.include_router(resources.router)
api_router.include_router(teams.router)
api_router.include_router(tasks.router)
api_router.include_router(coordination.router)
api_router.include_router(shelters.router)
api_router.include_router(alerts.router)
api_router.include_router(analytics.router)
api_router.include_router(audit_logs.router)
api_router.include_router(ai.router)
api_router.include_router(websockets.router)

