from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB, ENUM as PG_ENUM
from sqlalchemy.orm import relationship
from src.database import Base
import enum


class ConfigType(str, enum.Enum):
    """Enum for config type"""
    # Add your config types here
    # Example: SETTINGS = "settings", RULES = "rules", etc.
    pass


class ConfigStatus(str, enum.Enum):
    """Enum for config status"""
    ACTIVE = "active"
    INACTIVE = "inactive"


class SportConfig(Base):
    """
    Model for the sports_config table.
    
    Represents configuration details specific to each sport.
    
    Attributes:
        id: Primary key, auto-incrementing integer
        sport_id: Foreign key to sports table (INTEGER)
        config_type: Type of configuration (ENUM)
        config_data: Configuration data (JSONB)
        status: Config status (ENUM)
        created_at: Timestamp when config was created
        updated_at: Timestamp when config was last updated
        created_by: User ID who created the config (INTEGER)
        description: Config description (TEXT)
    """
    __tablename__ = "sports_config"
    __table_args__ = {"schema": "public"}

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )
    sport_id = Column(
        Integer,
        ForeignKey("public.sports.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    config_type = Column(
        PG_ENUM(ConfigType, name="config_type", create_type=False),
        nullable=False
    )
    config_data = Column(JSONB)
    status = Column(
        PG_ENUM(ConfigStatus, name="config_status", create_type=False),
        nullable=False,
        default=ConfigStatus.ACTIVE
    )
    created_at = Column(
        DateTime(timezone=False),
        server_default=func.current_timestamp(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=False),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False
    )
    created_by = Column(Integer)
    description = Column(Text)
    
    # Relationship to sport
    sport = relationship("Sport", back_populates="configs")

