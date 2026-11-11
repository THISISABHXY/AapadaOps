"""AapadaOps API v1 Dependencies: Authentication, RBAC, and Pagination."""

from typing import List, Optional
from fastapi import Depends, Header, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_token
from app.models.user import User, UserRole

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Validate JWT bearer token and inject active user into endpoint context."""
    if not credentials:
        raise UnauthorizedError("Authorization header with Bearer token is required.")

    token = credentials.credentials
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise UnauthorizedError("Invalid or expired session access token.")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError("Token subject is invalid.")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise UnauthorizedError("User associated with token no longer exists.")
    if not user.is_active:
        raise ForbiddenError("User account has been deactivated.")

    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """Extract user if valid token present, otherwise return None."""
    if not credentials:
        return None
    try:
        return await get_current_user(credentials=credentials, db=db)
    except Exception:
        return None


def require_roles(*allowed_roles: UserRole):
    """Enforce role-based access control. SUPER_ADMIN is always permitted."""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role == UserRole.SUPER_ADMIN:
            return current_user

        if current_user.role not in allowed_roles:
            role_names = ", ".join([r.value for r in allowed_roles])
            raise ForbiddenError(
                f"Operational permission denied. Role '{current_user.role.value}' does not have access. Required: [{role_names}]"
            )
        return current_user

    return role_checker


class PaginationParams:
    """Standard pagination query parameters."""

    def __init__(
        self,
        skip: int = Query(0, ge=0, description="Records to skip"),
        limit: int = Query(50, ge=1, le=200, description="Page limit"),
    ):
        self.skip = skip
        self.limit = limit

