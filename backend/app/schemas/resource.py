"""AapadaOps ODRN Resource, Team, Task, and Shelter Schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.resource import ResourceStatus, ResourceType
from app.models.team import TeamStatus
from app.models.task import TaskStatus
from app.models.shelter import ShelterStatus


# --- Resources ---
class ResourceCreate(BaseModel):
    name: str = Field(..., min_length=3)
    category: ResourceType
    organization: str
    district_name: str
    district_id: Optional[str] = None
    quantity: int = Field(default=1, ge=1)
    unit_of_measure: str = "units"
    latitude: float
    longitude: float
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None


class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[ResourceStatus] = None
    quantity: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None


class ResourceResponse(BaseModel):
    id: str
    code: str
    name: str
    category: ResourceType
    organization: str
    district_id: Optional[str] = None
    district_name: str
    status: ResourceStatus
    quantity: int
    unit_of_measure: str
    latitude: float
    longitude: float
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Response Teams ---
class TeamCreate(BaseModel):
    name: str = Field(..., min_length=3)
    organization: str
    battalion: Optional[str] = None
    team_lead_name: str
    team_lead_phone: str
    total_personnel: int = Field(default=10, ge=1)
    current_district_name: str
    current_district_id: Optional[str] = None
    latitude: float
    longitude: float


class TeamUpdate(BaseModel):
    status: Optional[TeamStatus] = None
    current_district_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    team_lead_phone: Optional[str] = None


class TeamResponse(BaseModel):
    id: str
    code: str
    name: str
    organization: str
    battalion: Optional[str] = None
    team_lead_name: str
    team_lead_phone: str
    total_personnel: int
    current_district_id: Optional[str] = None
    current_district_name: str
    latitude: float
    longitude: float
    status: TeamStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Tasks ---
class TaskCreate(BaseModel):
    incident_id: str
    assigned_team_id: Optional[str] = None
    title: str = Field(..., min_length=5)
    description: Optional[str] = None
    priority: str = "HIGH"
    sla_hours: int = Field(default=4, ge=1)
    target_village: str
    target_latitude: float
    target_longitude: float
    dispatch_notes: Optional[str] = None


class TaskUpdate(BaseModel):
    status: Optional[TaskStatus] = None
    resolution_notes: Optional[str] = None
    assigned_team_id: Optional[str] = None


class TaskResponse(BaseModel):
    id: str
    task_code: str
    incident_id: str
    assigned_team_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    priority: str
    sla_hours: int
    deadline: Optional[datetime] = None
    status: TaskStatus
    target_village: str
    target_latitude: float
    target_longitude: float
    dispatch_notes: Optional[str] = None
    resolution_notes: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_by_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Cyclone Shelters ---
class ShelterCreate(BaseModel):
    name: str = Field(..., min_length=3)
    district_name: str
    district_id: Optional[str] = None
    block_name: Optional[str] = None
    block_id: Optional[str] = None
    village: str
    capacity: int = Field(default=500, ge=50)
    latitude: float
    longitude: float
    has_power_backup: bool = True
    generator_fuel_hours: int = 24
    drinking_water_days: int = 5
    has_medical_kit: bool = True
    caretaker_name: str
    caretaker_phone: str


class ShelterUpdate(BaseModel):
    current_occupancy: Optional[int] = None
    status: Optional[ShelterStatus] = None
    generator_fuel_hours: Optional[int] = None
    drinking_water_days: Optional[int] = None
    has_medical_kit: Optional[bool] = None


class ShelterResponse(BaseModel):
    id: str
    code: str
    name: str
    district_id: Optional[str] = None
    district_name: str
    block_id: Optional[str] = None
    block_name: Optional[str] = None
    village: str
    capacity: int
    current_occupancy: int
    latitude: float
    longitude: float
    has_power_backup: bool
    generator_fuel_hours: int
    drinking_water_days: int
    has_medical_kit: bool
    caretaker_name: str
    caretaker_phone: str
    status: ShelterStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

