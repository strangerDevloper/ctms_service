from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID, uuid4
from src.crud.tenant import tenant as crud_tenant
from src.crud.tenant_sports_mapping import tenant_sports_mapping as crud_mapping
from src.models.tenants import Tenant, TenantStatus
from src.schema.tenant import TenantCreate, TenantUpdate, TenantResponse, TenantListResponse, TenantQueryParams
from src.schema.tenant_sports_mapping import TenantSportsMappingResponse
from src.utils.response import PaginatedData


class TenantService:
    """
    Service layer for Tenant operations.
    Contains business logic and validation.
    """
    
    @staticmethod
    async def get_tenant(
        db: AsyncSession,
        tenant_id: int,
        include_sports: bool = False
    ) -> Tenant:
        """
        Get a tenant by ID.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            include_sports: If True, include sports mappings in the response
            
        Returns:
            Tenant object (with sports_mappings loaded if include_sports is True)
            
        Raises:
            HTTPException: If tenant not found
        """
        tenant_obj = await crud_tenant.get(db=db, id=tenant_id)
        if not tenant_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tenant with ID {tenant_id} not found"
            )
        if tenant_obj.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tenant with ID {tenant_id} has been deleted"
            )
        
        # If include_sports is True, load the sports mappings
        if include_sports:
            # Reload tenant with sports_mappings relationship
            result = await db.execute(
                select(Tenant)
                .options(selectinload(Tenant.sports_mappings))
                .filter(Tenant.id == tenant_id)
            )
            tenant_obj = result.scalar_one()
        
        return tenant_obj
    
    @staticmethod
    async def get_tenants(
        db: AsyncSession,
        query_params: TenantQueryParams
    ) -> PaginatedData[TenantListResponse]:
        """
        Get multiple tenants with pagination and filters.
        
        Args:
            db: Database session
            query_params: Query parameters object containing filters and pagination
            
        Returns:
            PaginatedData containing list of TenantListResponse objects, total count, and pagination info
        """
        items, total_count = await crud_tenant.get_multi(
            db=db,
            query_params=query_params
        )
        
        # Convert SQLAlchemy models to Pydantic models
        tenant_list = [TenantListResponse.model_validate(tenant) for tenant in items]
        
        # Calculate has_next_page
        has_next_page = (query_params.skip + query_params.limit) < total_count
        
        return PaginatedData(
            items=tenant_list,
            total_count=total_count,
            has_next_page=has_next_page,
            skip=query_params.skip,
            limit=query_params.limit
        )
    
    @staticmethod
    async def get_tenant_by_code(db: AsyncSession, tenant_code: str) -> Tenant:
        """
        Get a tenant by tenant_code.
        
        Args:
            db: Database session
            tenant_code: Tenant code
            
        Returns:
            Tenant object
            
        Raises:
            HTTPException: If tenant not found
        """
        tenant_obj = await crud_tenant.get_by_code(db=db, tenant_code=tenant_code)
        if not tenant_obj or tenant_obj.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tenant with code '{tenant_code}' not found"
            )
        return tenant_obj
    
    @staticmethod
    async def get_tenant_by_uuid(db: AsyncSession, tenant_uuid: UUID) -> Tenant:
        """
        Get a tenant by tenant_uuid.
        
        Args:
            db: Database session
            tenant_uuid: Tenant UUID
            
        Returns:
            Tenant object
            
        Raises:
            HTTPException: If tenant not found
        """
        tenant_obj = await crud_tenant.get_by_uuid(db=db, tenant_uuid=str(tenant_uuid))
        if not tenant_obj or tenant_obj.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tenant with UUID '{tenant_uuid}' not found"
            )
        return tenant_obj
    
    @staticmethod
    async def create_tenant(db: AsyncSession, tenant_in: TenantCreate) -> Tenant:
        """
        Create a new tenant.
        
        Args:
            db: Database session
            tenant_in: Tenant creation data
            
        Returns:
            Created Tenant object
            
        Raises:
            HTTPException: If tenant_code already exists
        """
        # Check if tenant_code already exists
        existing_tenant = await crud_tenant.get_by_code(db=db, tenant_code=tenant_in.tenant_code)
        if existing_tenant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tenant with code '{tenant_in.tenant_code}' already exists"
            )
        
        # Generate UUID if not provided
        # Pydantic v2 uses model_dump instead of dict
        if hasattr(tenant_in, 'model_dump'):
            tenant_data = tenant_in.model_dump()
        else:
            tenant_data = tenant_in.dict()
        
        if not tenant_data.get('tenant_uuid'):
            tenant_data['tenant_uuid'] = uuid4()
        
        return await crud_tenant.create(db=db, obj_in=TenantCreate(**tenant_data))
    
    @staticmethod
    async def update_tenant(
        db: AsyncSession,
        tenant_id: int,
        tenant_in: TenantUpdate
    ) -> Tenant:
        """
        Update an existing tenant.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            tenant_in: Tenant update data
            
        Returns:
            Updated Tenant object
            
        Raises:
            HTTPException: If tenant not found or tenant_code conflict
        """
        tenant_obj = await TenantService.get_tenant(db=db, tenant_id=tenant_id)
        
        # Check if tenant_code is being updated and conflicts with existing
        if tenant_in.tenant_code and tenant_in.tenant_code != tenant_obj.tenant_code:
            existing_tenant = await crud_tenant.get_by_code(db=db, tenant_code=tenant_in.tenant_code)
            if existing_tenant and existing_tenant.id != tenant_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Tenant with code '{tenant_in.tenant_code}' already exists"
                )
        
        return await crud_tenant.update(db=db, db_obj=tenant_obj, obj_in=tenant_in)
    
    @staticmethod
    async def delete_tenant(db: AsyncSession, tenant_id: int, soft_delete: bool = True) -> Tenant:
        """
        Delete a tenant (soft delete by default).
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            soft_delete: If True, perform soft delete, else hard delete
            
        Returns:
            Deleted Tenant object
            
        Raises:
            HTTPException: If tenant not found
        """
        tenant_obj = await TenantService.get_tenant(db=db, tenant_id=tenant_id)
        
        if soft_delete:
            return await crud_tenant.soft_delete(db=db, id=tenant_id)
        else:
            return await crud_tenant.delete(db=db, id=tenant_id)
    
    @staticmethod
    async def get_active_tenants(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[Tenant]:
        """
        Get all active tenants.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of active Tenant objects
        """
        return await crud_tenant.get_active_tenants(db=db, skip=skip, limit=limit)
    
    @staticmethod
    async def get_tenants_by_status(
        db: AsyncSession,
        status: TenantStatus,
        skip: int = 0,
        limit: int = 100
    ) -> List[Tenant]:
        """
        Get tenants by status.
        
        Args:
            db: Database session
            status: Tenant status
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of Tenant objects with specified status
        """
        return await crud_tenant.get_by_status(db=db, status=status, skip=skip, limit=limit)


# Create an instance of TenantService
tenant_service = TenantService()

