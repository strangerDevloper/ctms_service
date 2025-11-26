from typing import List, Optional, Tuple
from sqlalchemy import select, or_, func, and_
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from src.crud.base import CRUDBase
from src.models.tenants import Tenant, TenantStatus
from src.models.tenant_sports_mapping import TenantSportsMapping
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
    
    async def validate_exists(
        self,
        db: AsyncSession,
        *,
        tenant_id: int
    ) -> bool:
        """
        Validate that tenant exists and is not deleted.
        
        Args:
            db: Database session
            tenant_id: Tenant ID to validate
            
        Returns:
            True if tenant exists and is not deleted, False otherwise
        """
        query = select(func.count(Tenant.id)).filter(
            and_(
                Tenant.id == tenant_id,
                Tenant.is_deleted == False
            )
        )
        result = await db.execute(query)
        count = result.scalar_one()
        return count > 0
    
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
    
    def _apply_filters(self, query, query_params: TenantQueryParams):
        """
        Apply all filters to a query.
        This method centralizes all filter logic so it can be reused for both count and data queries.
        
        Args:
            query: SQLAlchemy select query
            query_params: Query parameters object containing filters
            
        Returns:
            Query with filters applied
        """
        # Filter by sports_id (join with tenant_sports_mapping if provided)
        if query_params.sports_id is not None:
            query = query.join(
                TenantSportsMapping,
                Tenant.id == TenantSportsMapping.tenant_id
            ).filter(
                TenantSportsMapping.sport_id == query_params.sports_id
            )
        
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
        
        return query
    
    async def get_multi(
        self,
        db: AsyncSession,
        *,
        query_params: TenantQueryParams
    ) -> Tuple[List[Tenant], int]:
        """
        Get multiple tenants with pagination and filters.
        
        Args:
            db: Database session
            query_params: Query parameters object containing filters and pagination
            
        Returns:
            Tuple of (List of Tenant objects, total count)
        """
        # Build base query for data retrieval with all filters
        base_query = select(Tenant)
        base_query = self._apply_filters(base_query, query_params)
        
        # Get total count using the same filters
        # Use distinct count if we have a join (sports_id filter)
        if query_params.sports_id is not None:
            count_query = select(func.count(func.distinct(Tenant.id)))
        else:
            count_query = select(func.count(Tenant.id))
        
        # Apply the same filters to count query
        count_query = self._apply_filters(count_query, query_params)
        
        # Execute count query
        count_result = await db.execute(count_query)
        total_count = count_result.scalar_one()
        
        # Apply pagination to get items
        # Use distinct if we have a join to avoid duplicates
        if query_params.sports_id is not None:
            data_query = base_query.distinct().offset(query_params.skip).limit(query_params.limit)
        else:
            data_query = base_query.offset(query_params.skip).limit(query_params.limit)
        
        result = await db.execute(data_query)
        items = list(result.scalars().all())
        
        return items, total_count


# Create an instance of CRUDTenant
tenant = CRUDTenant(Tenant)

