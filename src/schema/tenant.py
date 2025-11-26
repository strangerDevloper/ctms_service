from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator
from uuid import UUID
from src.models.tenants import TenantStatus


class TenantBase(BaseModel):
    """Base schema for Tenant with common fields."""
    name: str = Field(..., min_length=1, max_length=50, description="Tenant name")
    tenant_code: str = Field(..., min_length=1, max_length=10, description="Unique tenant code")
    logo: Optional[str] = Field(None, description="Logo URL or path")
    address: Optional[str] = Field(None, description="Address information")
    email: Optional[EmailStr] = Field(None, max_length=50, description="Contact email")
    description: Optional[str] = Field(None, description="Tenant description")
    status: TenantStatus = Field(default=TenantStatus.ACTIVE, description="Tenant status")
    
    @validator('tenant_code')
    def validate_tenant_code(cls, v):
        """Validate tenant_code format."""
        if not v.isalnum() and '_' not in v:
            raise ValueError('tenant_code must be alphanumeric or contain underscores')
        return v.upper()  # Convert to uppercase


class TenantCreate(TenantBase):
    """Schema for creating a new tenant."""
    tenant_uuid: Optional[UUID] = Field(None, description="Tenant UUID (auto-generated if not provided)")


class TenantUpdate(BaseModel):
    """Schema for updating a tenant."""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    tenant_code: Optional[str] = Field(None, min_length=1, max_length=10)
    logo: Optional[str] = None
    address: Optional[str] = None
    email: Optional[EmailStr] = Field(None, max_length=50)
    description: Optional[str] = None
    status: Optional[TenantStatus] = None
    
    @validator('tenant_code')
    def validate_tenant_code(cls, v):
        """Validate tenant_code format."""
        if v is not None:
            if not v.isalnum() and '_' not in v:
                raise ValueError('tenant_code must be alphanumeric or contain underscores')
            return v.upper()
        return v


class TenantInDB(TenantBase):
    """Schema for tenant data in database."""
    id: int
    tenant_uuid: UUID
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    
    class Config:
        from_attributes = True  # Pydantic v2 equivalent of orm_mode


class TenantResponse(TenantInDB):
    """Schema for tenant API response."""
    pass


class TenantListResponse(BaseModel):
    """Simplified schema for tenant list response with only essential fields."""
    id: int
    name: str
    tenant_code: str
    status: TenantStatus
    
    class Config:
        from_attributes = True


class TenantQueryParams(BaseModel):
    """Query parameters schema for filtering and paginating tenants."""
    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum number of records to return")
    status: Optional[TenantStatus] = Field(default=None, description="Filter by tenant status")
    search_id: Optional[int] = Field(default=None, description="Search by tenant ID")
    search: Optional[str] = Field(default=None, description="Search by tenant name or code (case-insensitive partial match)")
    include_deleted: bool = Field(default=False, description="Include soft-deleted tenants")
    
    class Config:
        from_attributes = True

