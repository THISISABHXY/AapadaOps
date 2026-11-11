"""AapadaOps Secure File Upload and Storage Service."""

import hashlib
import os
import uuid
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile
from app.core.config import settings
from app.core.exceptions import AppException


class FileUploadService:
    """Manages file uploads with MIME validation, SHA256 verification, and path isolation."""

    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save_file(self, upload_file: UploadFile) -> Tuple[str, str, int, str]:
        """Validate, hash, and persist file securely. Returns (filename, relative_path, size_bytes, sha256)."""
        # Validate MIME type
        content_type = upload_file.content_type or "application/octet-stream"
        if content_type not in settings.ALLOWED_UPLOAD_MIME_TYPES:
            raise AppException(
                message=f"File type '{content_type}' is not permitted for emergency evidence.",
                status_code=400,
                code="INVALID_FILE_TYPE",
            )

        content = await upload_file.read()
        file_size = len(content)

        # Validate file size
        if file_size > settings.MAX_FILE_SIZE_BYTES:
            raise AppException(
                message=f"File size exceeds maximum permitted limit ({settings.MAX_FILE_SIZE_BYTES // (1024*1024)}MB).",
                status_code=400,
                code="FILE_TOO_LARGE",
            )

        # Calculate SHA-256 Checksum
        sha256 = hashlib.sha256(content).hexdigest()

        # Sanitize file extension
        original_ext = Path(upload_file.filename or "file").suffix.lower()
        if original_ext not in [".jpg", ".jpeg", ".png", ".webp", ".pdf", ".mp3", ".ogg", ".wav"]:
            original_ext = ".bin"

        # Unique safe storage filename
        safe_filename = f"{uuid.uuid4()}{original_ext}"
        destination = self.upload_dir / safe_filename

        with open(destination, "wb") as f:
            f.write(content)

        return upload_file.filename or safe_filename, str(destination), file_size, sha256


file_service = FileUploadService()
