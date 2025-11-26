from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from src.models.tenant_sports_mapping import MappingStatus


class TenantSportsMappingBase(BaseModel):
    """Base schema for TenantSportsMapping with common fields."""
    tenant_id: int = Field(..., description="Tenant ID")
    sport_id: int = Field(..., description="Sport ID")
    status: MappingStatus = Field(default=MappingStatus.ACTIVE, description="Mapping status")
    desciption: Optional[str] = Field(None, description="Mapping description")


class TenantSportsMappingCreate(TenantSportsMappingBase):
    """Schema for creating a new tenant-sport mapping."""
    created_by: Optional[int] = Field(None, description="User ID who created the mapping")


class TenantSportsMappingUpdate(BaseModel):
    """Schema for updating a tenant-sport mapping."""
    status: Optional[MappingStatus] = Field(None, description="Mapping status")
    desciption: Optional[str] = Field(None, description="Mapping description")
    updated_by: Optional[int] = Field(None, description="User ID who updated the mapping")


class TenantSportsMappingInDB(TenantSportsMappingBase):
    """Schema for tenant-sport mapping data in database."""
    id: int
    created_by: Optional[int]
    created_at: datetime
    updated_by: Optional[int]
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TenantSportsMappingResponse(TenantSportsMappingInDB):
    """Schema for tenant-sport mapping API response."""
    pass


class TenantSportsMappingListResponse(BaseModel):
    """Simplified schema for tenant-sport mapping list response."""
    id: int
    tenant_id: int
    sport_id: int
    status: MappingStatus
    
    class Config:
        from_attributes = True


class RegisterSportItem(BaseModel):
    """Schema for a single sport registration item."""
    sport_id: int = Field(..., description="Sport ID to register")
    desciption: Optional[str] = Field(None, description="Mapping description")


class RegisterSportRequest(BaseModel):
    """Schema for registering a single sport under a tenant."""
    sport_id: int = Field(..., description="Sport ID to register")
    status: Optional[MappingStatus] = Field(default=MappingStatus.ACTIVE, description="Mapping status")
    desciption: Optional[str] = Field(None, description="Mapping description")
    created_by: Optional[int] = Field(None, description="User ID who created the mapping")


class BulkRegisterSportRequest(BaseModel):
    """Schema for registering multiple sports under a tenant."""
    sports: List[RegisterSportItem] = Field(..., min_items=1, description="List of sports to register")
    created_by: Optional[int] = Field(default=1, description="User ID who created the mappings (default: 1)")

