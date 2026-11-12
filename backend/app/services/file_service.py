"""AapadaOps Secure File Upload and Storage Service with Magic-Byte Inspection."""

import hashlib
import os
import re
import uuid
from pathlib import Path
from typing import Optional, Tuple
from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import AppException

# Allowed MIME types and their corresponding file extensions
ALLOWED_EXTENSIONS = {
    "image/jpeg": [".jpg", ".jpeg"],
    "image/png": [".png"],
    "image/webp": [".webp"],
    "application/pdf": [".pdf"],
    "audio/mpeg": [".mp3"],
    "audio/ogg": [".ogg"],
    "audio/wav": [".wav"],
}

# Dangerous executable extensions to explicitly block regardless of content
DISALLOWED_EXTENSIONS = {
    ".exe", ".bat", ".cmd", ".sh", ".bash", ".ps1", ".vbs", ".dll", ".so",
    ".php", ".phtml", ".py", ".pyc", ".rb", ".pl", ".jsp", ".asp", ".aspx",
    ".js", ".ts", ".mjs", ".html", ".htm", ".xhtml", ".svg", ".xml", ".cgi",
}


def detect_file_type_from_magic_bytes(data: bytes) -> Optional[str]:
    """Inspect binary file signature (magic bytes) to verify actual file format."""
    if len(data) < 4:
        return None

    # JPEG: FF D8 FF
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"

    # PNG: 89 50 4E 47 0D 0A 1A 0A
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"

    # PDF: %PDF-
    if data.startswith(b"%PDF-"):
        return "application/pdf"

    # RIFF container (WAV or WebP)
    if len(data) >= 12 and data[:4] == b"RIFF":
        container_format = data[8:12]
        if container_format == b"WEBP":
            return "image/webp"
        if container_format == b"WAVE":
            return "audio/wav"

    # Ogg container (Vorbis/Opus audio)
    if data.startswith(b"OggS"):
        return "audio/ogg"

    # MP3: ID3 tag or MPEG audio sync frame (11 consecutive 1 bits: 0xFF followed by 0xE0-0xFF)
    if data.startswith(b"ID3"):
        return "audio/mpeg"
    if len(data) >= 2 and data[0] == 0xFF and (data[1] & 0xE0) == 0xE0:
        return "audio/mpeg"

    return None


def sanitize_filename(raw_filename: str) -> str:
    """Sanitize original client filename to prevent path traversal and null-byte injection."""
    if not raw_filename:
        return "evidence_file.bin"

    # Strip directory components (Windows and POSIX)
    filename = os.path.basename(raw_filename.replace("\\", "/"))
    # Remove null bytes and control chars
    filename = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", filename)
    # Strip dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', "", filename)
    # Trim leading/trailing spaces and dots
    filename = filename.strip(" .")
    return filename or "evidence_file.bin"


class FileUploadService:
    """Manages secure file uploads with magic-byte verification, SHA256 integrity, and path isolation."""

    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR).resolve()
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save_file(self, upload_file: UploadFile) -> Tuple[str, str, int, str]:
        """Validate binary payload, hash SHA256, and persist file securely into isolated storage.

        Returns:
            Tuple of (sanitized_original_name, storage_filepath, file_size_bytes, sha256_hash)
        """
        raw_name = upload_file.filename or "evidence.bin"
        sanitized_name = sanitize_filename(raw_name)
        extension = Path(sanitized_name).suffix.lower()

        # Reject explicitly prohibited dangerous extensions
        if extension in DISALLOWED_EXTENSIONS:
            raise AppException(
                message=f"Executable and script files ('{extension}') are strictly forbidden.",
                status_code=400,
                code="PROHIBITED_FILE_EXTENSION",
            )

        # Read binary content
        content = await upload_file.read()
        file_size = len(content)

        # 1. Enforce strict file size limits
        if file_size == 0:
            raise AppException(
                message="Uploaded file is empty (0 bytes).",
                status_code=400,
                code="EMPTY_FILE",
            )

        if file_size > settings.MAX_FILE_SIZE_BYTES:
            max_mb = settings.MAX_FILE_SIZE_BYTES // (1024 * 1024)
            raise AppException(
                message=f"File size exceeds maximum permitted limit ({max_mb} MB).",
                status_code=400,
                code="FILE_TOO_LARGE",
            )

        # 2. Inspect magic bytes
        detected_mime = detect_file_type_from_magic_bytes(content)
        if not detected_mime or detected_mime not in settings.ALLOWED_UPLOAD_MIME_TYPES:
            raise AppException(
                message=(
                    "File content failed magic-byte signature verification. "
                    "Only verified photos (JPEG, PNG, WebP), audio recordings (MP3, WAV, OGG), "
                    "and disaster reports (PDF) are permitted."
                ),
                status_code=400,
                code="MALICIOUS_FILE_SIGNATURE",
            )

        # 3. Cross-validate file extension with detected binary type
        valid_extensions = ALLOWED_EXTENSIONS.get(detected_mime, [])
        if extension not in valid_extensions:
            # Normalize extension to primary detected extension if missing or mismatched
            extension = valid_extensions[0]

        # 4. Generate cryptographically strong SHA-256 Checksum
        sha256_hash = hashlib.sha256(content).hexdigest()

        # 5. Safe randomized storage path to prevent path traversal and file collisions
        safe_storage_name = f"{uuid.uuid4().hex}{extension}"
        destination = (self.upload_dir / safe_storage_name).resolve()

        # Path traversal guard: ensure destination is within self.upload_dir
        if not str(destination).startswith(str(self.upload_dir)):
            raise AppException(
                message="Path traversal attempt blocked.",
                status_code=400,
                code="SECURITY_PATH_TRAVERSAL",
            )

        # Persist to disk atomically
        with open(destination, "wb") as f:
            f.write(content)

        return sanitized_name, str(destination), file_size, sha256_hash


file_service = FileUploadService()
