from sqlalchemy import Column, Integer, String
from src.database import Base


class GlobalStreaming(Base):
    """
    Model for the global_streaming table.
    
    Represents global streaming channel information with tenant association.
    
    Attributes:
        id: Primary key, auto-incrementing integer
        channel_arn: Unique channel ARN identifier (VARCHAR 255)
        tenant_name: Tenant name associated with the stream (VARCHAR 50)
    """
    __tablename__ = "global_streaming"
    __table_args__ = {"schema": "public"}  # Explicitly set schema if needed

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True  # PostgreSQL sequence will handle this
    )
    channel_arn = Column(
        String(255),
        nullable=False,
        unique=True
    )
    tenant_name = Column(
        String(50),
        nullable=False
    )

