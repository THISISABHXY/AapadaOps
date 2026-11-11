"""AapadaOps In-Memory & Redis-Compatible Rate Limiter."""

import time
from collections import defaultdict
from typing import Dict, List
from fastapi import Request
from app.core.config import settings
from app.core.exceptions import RateLimitExceededError


class SlidingWindowRateLimiter:
    """Sliding-window request tracker for DDoS & flood submission protection."""

    def __init__(self):
        # Maps client key -> list of float timestamps
        self._requests: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, key: str, max_requests: int, window_seconds: int = 60) -> bool:
        now = time.time()
        window_start = now - window_seconds

        # Clean entries outside window
        self._requests[key] = [t for t in self._requests[key] if t > window_start]

        if len(self._requests[key]) >= max_requests:
            return False

        self._requests[key].append(now)
        return True

    def check(self, request: Request, max_requests: int = 120, window_seconds: int = 60):
        """Enforce rate limit for an incoming request based on client host IP."""
        client_ip = request.client.host if request.client else "127.0.0.1"
        endpoint = request.url.path
        key = f"{client_ip}:{endpoint}"

        if not self.is_allowed(key, max_requests, window_seconds):
            raise RateLimitExceededError(retry_after_seconds=window_seconds)


rate_limiter = SlidingWindowRateLimiter()
