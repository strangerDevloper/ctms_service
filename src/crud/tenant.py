from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.crud.base import CRUDBase
from src.models.tenants import Tenant, TenantStatus
from src.schema.tenant import TenantCreate, TenantUpdate


class CRUDTenant(CRUDBase[Tenant, TenantCreate, TenantUpdate]):
    """
    CRUD operations for Tenant model.
    Extends base CRUD with tenant-specific operations.
    """
    
    async def get_by_code(self, db: AsyncSession, *, tenant_code: str) -> Optional[Tenant]:
        """Get tenant by tenant_code."""
        result = await db.execute(
            select(Tenant).filter(Tenant.tenant_code == tenant_code)
        )
        return result.scalar_one_or_none()
    
    async def get_by_uuid(self, db: AsyncSession, *, tenant_uuid: str) -> Optional[Tenant]:
        """Get tenant by tenant_uuid."""
        result = await db.execute(
            select(Tenant).filter(Tenant.tenant_uuid == tenant_uuid)
        )
        return result.scalar_one_or_none()
    
    async def get_active_tenants(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Tenant]:
        """Get all active tenants (not deleted and status is ACTIVE)."""
        query = (
            select(Tenant)
            .filter(Tenant.is_deleted == False)
            .filter(Tenant.status == TenantStatus.ACTIVE)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_status(
        self,
        db: AsyncSession,
        *,
        status: TenantStatus,
        skip: int = 0,
        limit: int = 100
    ) -> List[Tenant]:
        """Get tenants by status."""
        query = (
            select(Tenant)
            .filter(Tenant.status == status)
            .filter(Tenant.is_deleted == False)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False
    ) -> List[Tenant]:
        """
        Get multiple tenants with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_deleted: Whether to include soft-deleted tenants
        """
        query = select(Tenant)
        
        if not include_deleted:
            query = query.filter(Tenant.is_deleted == False)
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())


# Create an instance of CRUDTenant
tenant = CRUDTenant(Tenant)

