from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from src.database import Base


class Job(Base):
    """
    Model for the jobs table.
    
    Represents job/task tracking information with status, progress, and results.
    
    Attributes:
        id: Primary key, auto-incrementing integer
        task_id: Unique task identifier (VARCHAR 255)
        tenant_name: Tenant name associated with the job (VARCHAR 100)
        service_name: Service name that handles the job (VARCHAR 100)
        task_name: Name of the task (VARCHAR 255)
        status: Job status (VARCHAR 50), default 'pending'
        progress: Current progress value (integer), default 0
        total: Total progress value (integer), default 100
        result: Job result data (JSONB)
        error: Error message if job failed (TEXT)
        parameters: Job parameters (JSONB)
        created_at: Timestamp when job was created
        started_at: Timestamp when job started
        completed_at: Timestamp when job completed
        expires_at: Timestamp when job expires
    """
    __tablename__ = "jobs"
    __table_args__ = {"schema": "public"}

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )
    task_id = Column(
        String(255),
        nullable=False,
        unique=True,
        index=True  # Has explicit index idx_jobs_task_id
    )
    tenant_name = Column(
        String(100),
        nullable=False,
        index=True  # Has explicit index idx_jobs_tenant_name
    )
    service_name = Column(
        String(100),
        nullable=False
    )
    task_name = Column(
        String(255),
        nullable=False
    )
    status = Column(
        String(50),
        nullable=False,
        default="pending",
        index=True  # Has explicit index idx_jobs_status
    )
    progress = Column(
        Integer,
        default=0
    )
    total = Column(
        Integer,
        default=100
    )
    result = Column(JSONB)
    error = Column(Text)
    parameters = Column(JSONB)
    created_at = Column(
        DateTime(timezone=False),
        server_default=func.current_timestamp(),
        nullable=False
    )
    started_at = Column(DateTime(timezone=False))
    completed_at = Column(DateTime(timezone=False))
    expires_at = Column(DateTime(timezone=False))

