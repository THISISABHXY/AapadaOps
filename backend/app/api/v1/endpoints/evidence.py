"""AapadaOps Evidence Media Upload & Verification API."""

from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.api.v1.deps import get_current_user, get_optional_user
from app.models.evidence import EvidenceFile
from app.models.user import User
from app.schemas.report import EvidenceResponse
from app.services.file_service import file_service
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/evidence", tags=["Evidence & Media"])


@router.post("/upload", response_model=EvidenceResponse, status_code=status.HTTP_201_CREATED)
async def upload_evidence(
    file: UploadFile = File(...),
    incident_id: Optional[str] = Form(None),
    task_id: Optional[str] = Form(None),
    report_id: Optional[str] = Form(None),
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload photos, audio voice notes, or documents verifying ground conditions."""
    orig_name, storage_path, file_size, sha256 = await file_service.save_file(file)

    evidence = EvidenceFile(
        incident_id=incident_id,
        task_id=task_id,
        report_id=report_id,
        file_name=orig_name,
        file_path=storage_path,
        file_size_bytes=file_size,
        mime_type=file.content_type or "application/octet-stream",
        sha256_hash=sha256,
        uploader_id=current_user.id if current_user else None,
        is_verified=bool(current_user),
    )
    db.add(evidence)
    await db.flush()

    if current_user:
        await log_audit_event(
            db,
            action="UPLOAD_EVIDENCE",
            entity_type="EVIDENCE",
            entity_id=evidence.id,
            actor=current_user,
            description=f"Uploaded evidence file '{orig_name}' ({file_size // 1024} KB).",
            changes={"sha256": sha256, "mime_type": evidence.mime_type},
        )

    await db.commit()
    await db.refresh(evidence)
    return evidence


@router.get("/{evidence_id}/download")
async def download_evidence_file(evidence_id: str, db: AsyncSession = Depends(get_db)):
    """Stream raw evidence file to browser or mobile client."""
    result = await db.execute(select(EvidenceFile).where(EvidenceFile.id == evidence_id))
    evidence = result.scalar_one_or_none()
    if not evidence or not Path(evidence.file_path).exists():
        raise NotFoundError("EvidenceFile", evidence_id)

    return FileResponse(
        path=evidence.file_path,
        media_type=evidence.mime_type,
        filename=evidence.file_name,
    )

