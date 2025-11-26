from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.database import Base
import enum


class SportCategory(str, enum.Enum):
    """Enum for sport category"""
    # Add your sport categories here
    RACKET_SPORTS = "racket_sports"
    FIELD_SPORTS = "field_sports"
    MIXED_SPORTS = "mixed_sports"
    OTHER = "other"


class SportStatus(str, enum.Enum):
    """Enum for sport status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class Sport(Base):
    """
    Model for the sports table.
    
    Represents sport information.
    
    Attributes:
        id: Primary key, auto-incrementing integer
        sport_code: Unique sport code (VARCHAR 10)
        sport_name: Sport name (VARCHAR 25)
        category: Sport category (ENUM)
        icon_url: Icon URL or path (TEXT)
        status: Sport status (ENUM)
        description: Sport description (TEXT)
        created_at: Timestamp when sport was created
        updated_at: Timestamp when sport was last updated
        is_deleted: Soft delete flag (BOOLEAN)
    """
    __tablename__ = "sports"
    __table_args__ = {"schema": "public"}

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )
    sport_code = Column(
        String(10),
        nullable=False,
        unique=True,
        index=True
    )
    sport_name = Column(
        String(25),
        nullable=False
    )
    category = Column(
        PG_ENUM(SportCategory, name="sport_category", create_type=False),
        nullable=True
    )
    icon_url = Column(Text)
    status = Column(
        PG_ENUM(SportStatus, name="sport_status", create_type=False),
        nullable=False,
        default=SportStatus.ACTIVE
    )
    description = Column(Text)
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
    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False
    )
    
    # Relationships
    configs = relationship("SportConfig", back_populates="sport")
    tenant_mappings = relationship("TenantSportsMapping", back_populates="sport")

