from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator
from src.models.sports import SportCategory, SportStatus
from src.schema.sports_config import SportConfigResponse


class SportBase(BaseModel):
    """Base schema for Sport with common fields."""
    sport_code: str = Field(..., min_length=1, max_length=10, description="Unique sport code")
    sport_name: str = Field(..., min_length=1, max_length=25, description="Sport name")
    category: Optional[SportCategory] = Field(None, description="Sport category")
    icon_url: Optional[str] = Field(None, description="Icon URL or path")
    status: SportStatus = Field(default=SportStatus.ACTIVE, description="Sport status")
    description: Optional[str] = Field(None, description="Sport description")
    
    @validator('sport_code')
    def validate_sport_code(cls, v):
        """Validate sport_code format."""
        if not v.isalnum() and '_' not in v:
            raise ValueError('sport_code must be alphanumeric or contain underscores')
        return v.upper()  # Convert to uppercase


class SportCreate(SportBase):
    """Schema for creating a new sport."""
    pass


class SportUpdate(BaseModel):
    """Schema for updating a sport."""
    sport_code: Optional[str] = Field(None, min_length=1, max_length=10)
    sport_name: Optional[str] = Field(None, min_length=1, max_length=25)
    category: Optional[SportCategory] = None
    icon_url: Optional[str] = None
    status: Optional[SportStatus] = None
    description: Optional[str] = None
    
    @validator('sport_code')
    def validate_sport_code(cls, v):
        """Validate sport_code format."""
        if v is not None:
            if not v.isalnum() and '_' not in v:
                raise ValueError('sport_code must be alphanumeric or contain underscores')
            return v.upper()
        return v


class SportInDB(SportBase):
    """Schema for sport data in database."""
    id: int
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    
    class Config:
        from_attributes = True  # Pydantic v2 equivalent of orm_mode


class SportResponse(SportInDB):
    """Schema for sport API response."""
    configs: Optional[List[SportConfigResponse]] = Field(None, description="List of sport configs (optional)")
    
    class Config:
        from_attributes = True


class SportListResponse(BaseModel):
    """Simplified schema for sport list response with only essential fields."""
    id: int
    sport_code: str
    sport_name: str
    category: Optional[SportCategory]
    status: SportStatus
    
    class Config:
        from_attributes = True


class SportQueryParams(BaseModel):
    """Query parameters schema for filtering and paginating sports."""
    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum number of records to return")
    status: Optional[SportStatus] = Field(default=None, description="Filter by sport status")
    category: Optional[SportCategory] = Field(default=None, description="Filter by sport category")
    search_id: Optional[int] = Field(default=None, description="Search by sport ID")
    search: Optional[str] = Field(default=None, description="Search by sport name or code (case-insensitive partial match)")
    include_deleted: bool = Field(default=False, description="Include soft-deleted sports")
    
    class Config:
        from_attributes = True

