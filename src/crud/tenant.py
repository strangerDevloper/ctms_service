from typing import List, Optional
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from src.crud.base import CRUDBase
from src.models.tenants import Tenant, TenantStatus
from src.schema.tenant import TenantCreate, TenantUpdate, TenantQueryParams


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
        query_params: TenantQueryParams
    ) -> List[Tenant]:
        """
        Get multiple tenants with pagination and filters.
        
        Args:
            db: Database session
            query_params: Query parameters object containing filters and pagination
            
        Returns:
            List of Tenant objects
        """
        query = select(Tenant)
        
        # Filter by deleted status
        if not query_params.include_deleted:
            query = query.filter(Tenant.is_deleted == False)
        
        # Filter by status
        if query_params.status is not None:
            query = query.filter(Tenant.status == query_params.status)
        
        # Filter by ID
        if query_params.search_id is not None:
            query = query.filter(Tenant.id == query_params.search_id)
        
        # Search by name or code (case-insensitive partial match)
        if query_params.search:
            search_pattern = f"%{query_params.search}%"
            query = query.filter(
                or_(
                    Tenant.name.ilike(search_pattern),
                    Tenant.tenant_code.ilike(search_pattern)
                )
            )
        
        # Apply pagination
        query = query.offset(query_params.skip).limit(query_params.limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())


# Create an instance of CRUDTenant
tenant = CRUDTenant(Tenant)

