from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.database import Base
import enum


class MappingStatus(str, enum.Enum):
    """Enum for tenant sports mapping status"""
    ACTIVE = "active"
    INACTIVE = "inactive"


class TenantSportsMapping(Base):
    """
    Model for the tenant_sports_mapping table.
    
    Represents the mapping between tenants and sports.
    
    Attributes:
        id: Primary key, auto-incrementing integer
        tenant_id: Foreign key to tenants table (INTEGER)
        sport_id: Foreign key to sports table (INTEGER)
        status: Mapping status (ENUM)
        created_by: User ID who created the mapping (INTEGER)
        created_at: Timestamp when mapping was created
        updated_by: User ID who last updated the mapping (INTEGER)
        updated_at: Timestamp when mapping was last updated
        desciption: Description of the mapping (TEXT) - Note: typo in original schema
    """
    __tablename__ = "tenant_sports_mapping"
    __table_args__ = {"schema": "public"}

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )
    tenant_id = Column(
        Integer,
        ForeignKey("public.tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    sport_id = Column(
        Integer,
        ForeignKey("public.sports.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    status = Column(
        PG_ENUM(MappingStatus, name="mapping_status", create_type=False),
        nullable=False,
        default=MappingStatus.ACTIVE
    )
    created_by = Column(Integer)
    created_at = Column(
        DateTime(timezone=False),
        server_default=func.current_timestamp(),
        nullable=False
    )
    updated_by = Column(Integer)
    updated_at = Column(
        DateTime(timezone=False),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False
    )
    desciption = Column(Text)  # Note: Keeping original typo from schema
    
    # Relationships
    tenant = relationship("Tenant", back_populates="sports_mappings")
    sport = relationship("Sport", back_populates="tenant_mappings")

