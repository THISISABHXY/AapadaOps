"""AapadaOps Field Reports API."""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.api.v1.deps import get_optional_user
from app.models.incident import Incident
from app.models.report import IncidentReport
from app.models.user import User
from app.schemas.report import ReportCreate, ReportResponse
from app.services.ai_service import ai_engine

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def submit_report(
    report_in: ReportCreate,
    current_user: User = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """Attach supplemental field or citizen report to an existing incident."""
    result = await db.execute(select(Incident).where(Incident.id == report_in.incident_id))
    incident = result.scalar_one_or_none()
    if not incident:
        raise NotFoundError("Incident", report_in.incident_id)

    # Detect language
    lang = ai_engine.detect_language(report_in.raw_text)

    report = IncidentReport(
        incident_id=incident.id,
        source_type=report_in.source_type,
        raw_text=report_in.raw_text,
        text_language=lang,
        audio_url=report_in.audio_url,
        transcript_text=report_in.transcript_text,
        reporter_name=report_in.reporter_name,
        reporter_phone=report_in.reporter_phone,
        gps_lat=report_in.gps_lat,
        gps_lng=report_in.gps_lng,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report


@router.get("/incident/{incident_id}", response_model=List[ReportResponse])
async def get_incident_reports(incident_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve all reports and updates submitted for an incident."""
    result = await db.execute(
        select(IncidentReport)
        .where(IncidentReport.incident_id == incident_id)
        .order_by(IncidentReport.created_at.desc())
    )
    return result.scalars().all()
