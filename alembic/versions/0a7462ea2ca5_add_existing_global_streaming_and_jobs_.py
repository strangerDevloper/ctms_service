"""Add existing global_streaming and jobs tables

Revision ID: 0a7462ea2ca5
Revises: 6fdefa942e27
Create Date: 2025-11-24 17:06:36.661359

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = '0a7462ea2ca5'
down_revision: Union[str, None] = '6fdefa942e27'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if tables already exist before creating them
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_tables = inspector.get_table_names(schema='public')
    
    # Create global_streaming table if it doesn't exist
    if 'global_streaming' not in existing_tables:
        op.create_table('global_streaming',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('channel_arn', sa.String(length=255), nullable=False),
            sa.Column('tenant_name', sa.String(length=50), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('channel_arn'),
            schema='public'
        )
        op.create_index(op.f('ix_public_global_streaming_id'), 'global_streaming', ['id'], unique=False, schema='public')
    else:
        print("Table 'global_streaming' already exists, skipping creation.")
    
    # Create jobs table if it doesn't exist
    if 'jobs' not in existing_tables:
        op.create_table('jobs',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('task_id', sa.String(length=255), nullable=False),
            sa.Column('tenant_name', sa.String(length=100), nullable=False),
            sa.Column('service_name', sa.String(length=100), nullable=False),
            sa.Column('task_name', sa.String(length=255), nullable=False),
            sa.Column('status', sa.String(length=50), nullable=False),
            sa.Column('progress', sa.Integer(), nullable=True),
            sa.Column('total', sa.Integer(), nullable=True),
            sa.Column('result', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column('error', sa.Text(), nullable=True),
            sa.Column('parameters', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
            sa.Column('started_at', sa.DateTime(), nullable=True),
            sa.Column('completed_at', sa.DateTime(), nullable=True),
            sa.Column('expires_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            schema='public'
        )
        op.create_index(op.f('ix_public_jobs_id'), 'jobs', ['id'], unique=False, schema='public')
        op.create_index(op.f('ix_public_jobs_status'), 'jobs', ['status'], unique=False, schema='public') 
        op.create_index(op.f('ix_public_jobs_task_id'), 'jobs', ['task_id'], unique=True, schema='public')
        op.create_index(op.f('ix_public_jobs_tenant_name'), 'jobs', ['tenant_name'], unique=False, schema='public')
    else:
        print("Table 'jobs' already exists, skipping creation.")


def downgrade() -> None:
    # Check if tables exist before dropping them
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_tables = inspector.get_table_names(schema='public')
    
    # Drop jobs table if it exists
    if 'jobs' in existing_tables:
        op.drop_index(op.f('ix_public_jobs_tenant_name'), table_name='jobs', schema='public')
        op.drop_index(op.f('ix_public_jobs_task_id'), table_name='jobs', schema='public')
        op.drop_index(op.f('ix_public_jobs_status'), table_name='jobs', schema='public')
        op.drop_index(op.f('ix_public_jobs_id'), table_name='jobs', schema='public')
        op.drop_table('jobs', schema='public')
    
    # Drop global_streaming table if it exists
    if 'global_streaming' in existing_tables:
        op.drop_index(op.f('ix_public_global_streaming_id'), table_name='global_streaming', schema='public')
        op.drop_table('global_streaming', schema='public')
