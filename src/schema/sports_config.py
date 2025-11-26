from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from src.models.sports_config import ConfigStatus


class SportConfigBase(BaseModel):
    """Base schema for SportConfig with common fields."""
    sport_id: int = Field(..., description="Foreign key to sports table")
    config_type: str = Field(..., description="Type of configuration")
    config_data: Optional[Dict[str, Any]] = Field(None, description="Configuration data (JSONB)")
    status: ConfigStatus = Field(default=ConfigStatus.ACTIVE, description="Config status")
    created_by: Optional[int] = Field(None, description="User ID who created the config")
    description: Optional[str] = Field(None, description="Config description")


class SportConfigCreate(SportConfigBase):
    """Schema for creating a new sport config."""
    pass


class SportConfigCreateWithoutSportId(BaseModel):
    """Schema for creating a sport config without sport_id (sport_id comes from path)."""
    config_type: str = Field(..., description="Type of configuration")
    config_data: Optional[Dict[str, Any]] = Field(None, description="Configuration data (JSONB)")
    status: ConfigStatus = Field(default=ConfigStatus.ACTIVE, description="Config status")
    created_by: Optional[int] = Field(None, description="User ID who created the config")
    description: Optional[str] = Field(None, description="Config description")


class SportConfigBulkCreate(BaseModel):
    """Schema for bulk creating sport configs (sport_id comes from path parameter)."""
    configs: List[SportConfigCreateWithoutSportId] = Field(..., min_items=1, description="List of configs to create")


class SportConfigUpdate(BaseModel):
    """Schema for updating a sport config."""
    config_type: Optional[str] = Field(None, description="Type of configuration")
    config_data: Optional[Dict[str, Any]] = Field(None, description="Configuration data (JSONB)")
    status: Optional[ConfigStatus] = Field(None, description="Config status")
    description: Optional[str] = Field(None, description="Config description")


class SportConfigInDB(SportConfigBase):
    """Schema for sport config data in database."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  # Pydantic v2 equivalent of orm_mode


class SportConfigResponse(SportConfigInDB):
    """Schema for sport config API response."""
    pass


class SportConfigListResponse(BaseModel):
    """Schema for list of sport configs."""
    items: List[SportConfigResponse]
    total_count: int
    
    class Config:
        from_attributes = True

