# Import all models here so Alembic can detect them
from src.models.global_streaming import GlobalStreaming
from src.models.jobs import Job
from src.models.tenants import Tenant, TenantStatus
from src.models.tenant_sports_mapping import TenantSportsMapping, MappingStatus
from src.models.sports import Sport, SportCategory, SportStatus
from src.models.sports_config import SportConfig, ConfigType, ConfigStatus

__all__ = [
    "GlobalStreaming",
    "Job",
    "Tenant",
    "TenantStatus",
    "TenantSportsMapping",
    "MappingStatus",
    "Sport",
    "SportCategory",
    "SportStatus",
    "SportConfig",
    "ConfigType",
    "ConfigStatus"
]

