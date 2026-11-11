"""AapadaOps Administrative Geography Schemas."""

from typing import List, Optional
from pydantic import BaseModel


class BlockResponse(BaseModel):
    id: str
    name: str
    name_odia: Optional[str] = None
    gram_panchayats_count: int
    is_coastal: bool

    model_config = {"from_attributes": True}


class DistrictResponse(BaseModel):
    id: str
    code: str
    name: str
    name_odia: Optional[str] = None
    headquarters: str
    population: int
    coastal_zone: bool
    vulnerability_tier: int
    center_lat: float
    center_lng: float

    model_config = {"from_attributes": True}


class DistrictDetailResponse(DistrictResponse):
    blocks: List[BlockResponse] = []
