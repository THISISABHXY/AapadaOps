"""AapadaOps Administrative Geography: Districts and Blocks."""

from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class District(BaseModel):
    """District administrative boundary in Odisha (30 districts)."""

    __tablename__ = "districts"

    code = Column(String(10), unique=True, index=True, nullable=False)
    name = Column(String(100), unique=True, index=True, nullable=False)
    name_odia = Column(String(100), nullable=True)
    headquarters = Column(String(100), nullable=False)
    population = Column(Integer, default=0, nullable=False)
    coastal_zone = Column(Boolean, default=False, index=True, nullable=False)
    vulnerability_tier = Column(Integer, default=1, nullable=False)  # 1 (lowest) to 5 (highest, e.g. Kendrapara/Bhadrak)
    center_lat = Column(Float, nullable=False)
    center_lng = Column(Float, nullable=False)
    bounds_geojson = Column(Text, nullable=True)

    # Relationships
    blocks = relationship("Block", back_populates="district", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<District {self.name} ({self.code})>"


class Block(BaseModel):
    """Sub-district administrative block in Odisha (314 blocks)."""

    __tablename__ = "blocks"

    district_id = Column(String(36), ForeignKey("districts.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), index=True, nullable=False)
    name_odia = Column(String(100), nullable=True)
    gram_panchayats_count = Column(Integer, default=0, nullable=False)
    is_coastal = Column(Boolean, default=False, nullable=False)

    # Relationships
    district = relationship("District", back_populates="blocks")

    def __repr__(self) -> str:
        return f"<Block {self.name} in {self.district_id}>"

