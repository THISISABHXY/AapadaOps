"""Tests for Rate Limiting, File Upload Validations, and AI Text Processing."""

import pytest
from httpx import AsyncClient
from app.core.exceptions import RateLimitExceededError
from app.core.rate_limiter import SlidingWindowRateLimiter


def test_sliding_window_rate_limiter():
    """Verify rate limiter allows requests up to max_requests and rejects excess."""
    limiter = SlidingWindowRateLimiter()
    key = "test-client-ip:/api/test"

    for _ in range(5):
        assert limiter.is_allowed(key, max_requests=5, window_seconds=60) is True

    # 6th request must be rejected
    assert limiter.is_allowed(key, max_requests=5, window_seconds=60) is False


@pytest.mark.asyncio
async def test_ai_text_analysis_endpoint(client: AsyncClient):
    """Verify bilingual analysis endpoint returns structured advisory."""
    # Test Odia text: "ବନ୍ୟା ପାଣିରେ ୨୦ ଜଣ ଲୋକ ଫସି ରହିଛନ୍ତି" (20 people stranded in flood water)
    response = await client.post(
        "/api/v1/ai/analyze-text",
        json={"text": "ବନ୍ୟା ପାଣିରେ ୨୦ ଜଣ ଲୋକ ଫସି ରହିଛନ୍ତି"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["detected_language"] == "or"
    assert data["suggested_category"] in ("FLOOD", "STRANDED_PERSONS")
    assert data["is_ai_generated"] is True
    assert "AI Advisory:" in data["ai_advisory_statement"]


@pytest.mark.asyncio
async def test_evidence_file_upload(client: AsyncClient):
    """Verify secure evidence upload validates file size and computes SHA256 checksum."""
    dummy_image = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"
    files = {"file": ("damage_photo.png", dummy_image, "image/png")}

    response = await client.post("/api/v1/evidence/upload", files=files)
    assert response.status_code == 201
    data = response.json()
    assert data["file_name"] == "damage_photo.png"
    assert data["mime_type"] == "image/png"
    assert len(data["sha256_hash"]) == 64

