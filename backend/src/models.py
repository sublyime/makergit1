from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import List, Optional

class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[EmailStr] = None
    display_name: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class UserRead(BaseModel):
    id: str
    username: str
    email: Optional[EmailStr] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    website_url: Optional[str] = None
    location: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    api_key: str

class RegisterResponse(UserRead):
    api_key: str

class ProjectBase(BaseModel):
    title: str
    summary: Optional[str] = None
    description: Optional[str] = None
    visibility: str = "public"
    status: str = "planning"
    tags: Optional[List[str]] = []

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    visibility: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None

class ProjectRead(ProjectBase):
    id: str
    owner_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Device Management Models
class DeviceCreate(BaseModel):
    name: str
    device_type: str
    unique_id: str
    config: Optional[dict] = None
    metadata: Optional[dict] = None

class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    firmware_version: Optional[str] = None
    config: Optional[dict] = None
    ip_address: Optional[str] = None

class DeviceRead(BaseModel):
    id: str
    project_id: str
    unique_id: str
    name: str
    device_type: str
    status: str
    last_seen: Optional[datetime] = None
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    firmware_version: Optional[str] = None
    config: Optional[dict] = None
    metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Firmware Management Models
class FirmwareVersionCreate(BaseModel):
    version: str
    description: Optional[str] = None
    binary_url: str
    checksum: Optional[str] = None
    size_bytes: Optional[int] = None
    from_commit: Optional[str] = None
    is_stable: bool = False
    release_notes: Optional[str] = None

class FirmwareVersionRead(BaseModel):
    id: str
    project_id: str
    version: str
    description: Optional[str] = None
    binary_url: str
    checksum: Optional[str] = None
    size_bytes: Optional[int] = None
    build_timestamp: Optional[datetime] = None
    from_commit: Optional[str] = None
    is_stable: bool
    release_notes: Optional[str] = None
    created_by: str
    created_at: datetime

    class Config:
        from_attributes = True

# Firmware Deployment Models
class FirmwareDeploymentRead(BaseModel):
    id: str
    device_id: str
    firmware_version_id: str
    status: str
    deployed_at: Optional[datetime] = None
    last_error: Optional[str] = None
    retry_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Device Telemetry Models
class TelemetryDataCreate(BaseModel):
    metric_name: str
    metric_value: dict
    tags: Optional[dict] = None

class TelemetryDataRead(BaseModel):
    id: str
    device_id: str
    timestamp: datetime
    metric_name: str
    metric_value: dict
    tags: Optional[dict] = None

    class Config:
        from_attributes = True

# Device Status/Health Model
class DeviceHealthRead(BaseModel):
    device_id: str
    device_name: str
    status: str
    firmware_version: Optional[str] = None
    last_seen: Optional[datetime] = None
    uptime_seconds: Optional[int] = None
    error_count: Optional[int] = None

# ===== BOM (Bill of Materials) Models =====

# Component Library Models
class ComponentLibraryCreate(BaseModel):
    part_number: str
    name: str
    category: str
    manufacturer: Optional[str] = None
    description: Optional[str] = None
    datasheet_url: Optional[str] = None
    pinout_diagram_url: Optional[str] = None
    specifications: Optional[dict] = None
    package_type: Optional[str] = None

class ComponentLibraryRead(BaseModel):
    id: str
    part_number: str
    name: str
    category: str
    manufacturer: Optional[str] = None
    description: Optional[str] = None
    datasheet_url: Optional[str] = None
    pinout_diagram_url: Optional[str] = None
    specifications: Optional[dict] = None
    package_type: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# BOM Item Models
class BOMItemCreate(BaseModel):
    reference: str
    description: str
    quantity: int = 1
    part_number: Optional[str] = None
    manufacturer: Optional[str] = None
    unit_price: Optional[float] = None
    supplier: Optional[str] = None
    supplier_url: Optional[str] = None
    lead_time_days: Optional[int] = None
    datasheet_url: Optional[str] = None
    notes: Optional[str] = None
    component_library_id: Optional[str] = None

class BOMItemUpdate(BaseModel):
    reference: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[int] = None
    part_number: Optional[str] = None
    manufacturer: Optional[str] = None
    unit_price: Optional[float] = None
    supplier: Optional[str] = None
    supplier_url: Optional[str] = None
    notes: Optional[str] = None

class BOMItemRead(BaseModel):
    id: str
    bom_id: str
    reference: str
    description: str
    quantity: int
    part_number: Optional[str] = None
    manufacturer: Optional[str] = None
    unit_price: Optional[float] = None
    total_price: Optional[float] = None
    supplier: Optional[str] = None
    supplier_url: Optional[str] = None
    lead_time_days: Optional[int] = None
    datasheet_url: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# BOM Models
class BOMCreate(BaseModel):
    name: str
    description: Optional[str] = None
    device_id: Optional[str] = None
    version: str = "1.0.0"

class BOMUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    estimated_cost: Optional[float] = None
    is_locked: Optional[bool] = None

class BOMRead(BaseModel):
    id: str
    project_id: str
    device_id: Optional[str] = None
    version: str
    name: str
    description: Optional[str] = None
    estimated_cost: Optional[float] = None
    is_locked: bool
    created_by: str
    created_at: datetime
    updated_at: datetime
    items: Optional[List[BOMItemRead]] = []

    class Config:
        from_attributes = True

# Component Variant Models
class ComponentVariantCreate(BaseModel):
    original_item_id: str
    variant_name: str
    alternative_part_number: str
    alternative_manufacturer: Optional[str] = None
    reason_for_variant: Optional[str] = None
    cost_delta: Optional[float] = None
    performance_impact: Optional[str] = None
    availability_status: Optional[str] = None

class ComponentVariantRead(BaseModel):
    id: str
    bom_id: str
    original_item_id: str
    variant_name: str
    alternative_part_number: str
    alternative_manufacturer: Optional[str] = None
    reason_for_variant: Optional[str] = None
    cost_delta: Optional[float] = None
    performance_impact: Optional[str] = None
    availability_status: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# BOM Summary Models
class BOMMaterialCostSummary(BaseModel):
    total_items: int
    unique_parts: int
    total_cost: float
    average_unit_cost: float
    longest_lead_time_days: Optional[int] = None
    suppliers: List[str] = []

class BOMForkRequest(BaseModel):
    new_name: str
    new_version: str
    new_device_id: Optional[str] = None
