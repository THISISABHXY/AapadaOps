"""AapadaOps Base Model Class and Timestamp Mixin."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, String
from app.core.database import Base


def generate_uuid() -> str:
    """Generate standardized lowercase UUID4 string."""
    return str(uuid.uuid4())


class TimestampMixin:
    """Provides created_at and updated_at timezone-aware timestamps."""

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class BaseModel(Base, TimestampMixin):
    """Abstract base model with UUID primary key."""

    __abstract__ = True

    id = Column(
        String(36),
        primary_key=True,
        default=generate_uuid,
        index=True,
    )

    def to_dict(self) -> dict:
        """Convert model attributes to dictionary."""
        return {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
        }

