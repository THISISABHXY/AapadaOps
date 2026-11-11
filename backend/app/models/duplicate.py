"""AapadaOps Spatial-Temporal Incident Duplicate Clusters."""

import enum
from sqlalchemy import Column, Enum, Float, ForeignKey, Integer, String, Text
from app.models.base import BaseModel


class ClusterStatus(str, enum.Enum):
    PENDING_REVIEW = "PENDING_REVIEW"
    CONFIRMED_MERGED = "CONFIRMED_MERGED"
    DISMISSED = "DISMISSED"


class DuplicateCluster(BaseModel):
    """Cluster of potential duplicate incidents detected within 500m / 24hr window."""

    __tablename__ = "duplicate_clusters"

    primary_incident_id = Column(
        String(36),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status = Column(
        Enum(ClusterStatus, name="cluster_status_enum"),
        default=ClusterStatus.PENDING_REVIEW,
        nullable=False,
        index=True,
    )
    spatial_radius_meters = Column(Float, default=500.0, nullable=False)
    confidence_score = Column(Float, default=0.0, nullable=False)
    cluster_summary = Column(Text, nullable=True)
    duplicate_count = Column(Integer, default=1, nullable=False)

    def __repr__(self) -> str:
        return f"<DuplicateCluster for {self.primary_incident_id} ({self.status})>"
