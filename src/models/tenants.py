from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID, ENUM as PG_ENUM
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.database import Base
import enum


class TenantStatus(str, enum.Enum):
    """Enum for tenant status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
    ON_HOLD = "on_hold"


class Tenant(Base):
    """
    Model for the tenants table.
    
    Represents tenant/organization information.
    
    Attributes:
        id: Primary key, auto-incrementing integer
        name: Tenant name (VARCHAR 50)
        tenant_code: Unique tenant code (VARCHAR 10)
        logo: Logo URL or path (TEXT)
        address: Address information (TEXT)
        tenant_uuid: Unique UUID identifier (UUID)
        email: Contact email (VARCHAR 50)
        description: Tenant description (TEXT)
        status: Tenant status (ENUM)
        created_at: Timestamp when tenant was created
        updated_at: Timestamp when tenant was last updated
        is_deleted: Soft delete flag (BOOLEAN)
    """
    __tablename__ = "tenants"
    __table_args__ = {"schema": "public"}

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )
    name = Column(
        String(50),
        nullable=False
    )
    tenant_code = Column(
        String(10),
        nullable=False,
        unique=True,
        index=True
    )
    logo = Column(Text)
    address = Column(Text)
    tenant_uuid = Column(
        UUID(as_uuid=True),
        nullable=False,
        unique=True
    )
    email = Column(String(50))
    description = Column(Text)
    status = Column(
        PG_ENUM(TenantStatus, name="tenant_status", create_type=False),
        nullable=False,
        default=TenantStatus.ACTIVE
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
    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False
    )
    
    # Relationship to tenant_sports_mapping
    sports_mappings = relationship("TenantSportsMapping", back_populates="tenant")

