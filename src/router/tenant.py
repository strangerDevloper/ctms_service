from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.service.tenant import tenant_service
from src.schema.tenant import TenantCreate, TenantUpdate, TenantResponse
from src.models.tenants import TenantStatus

router = APIRouter(
    prefix="/tenant",
    tags=["Tenants"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "",
    response_model=TenantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new tenant",
    description="Create a new tenant with the provided information"
)
async def create_tenant(
    *,
    db: AsyncSession = Depends(get_db),
    tenant_in: TenantCreate
):
    """Create a new tenant."""
    return await tenant_service.create_tenant(db=db, tenant_in=tenant_in)


@router.get(
    "",
    response_model=List[TenantResponse],
    summary="Get all tenants",
    description="Retrieve a list of tenants with pagination"
)
async def get_tenants(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    include_deleted: bool = Query(False, description="Include soft-deleted tenants"),
    db: AsyncSession = Depends(get_db)
):
    """Get all tenants with pagination."""
    return await tenant_service.get_tenants(
        db=db,
        skip=skip,
        limit=limit,
        include_deleted=include_deleted
    )


@router.get(
    "/active",
    response_model=List[TenantResponse],
    summary="Get active tenants",
    description="Retrieve a list of active tenants (not deleted and status is ACTIVE)"
)
async def get_active_tenants(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get all active tenants."""
    return await tenant_service.get_active_tenants(db=db, skip=skip, limit=limit)


@router.get(
    "/status/{status}",
    response_model=List[TenantResponse],
    summary="Get tenants by status",
    description="Retrieve tenants filtered by status"
)
async def get_tenants_by_status(
    status: TenantStatus,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get tenants by status."""
    return await tenant_service.get_tenants_by_status(
        db=db,
        status=status,
        skip=skip,
        limit=limit
    )


@router.get(
    "/{tenant_id}",
    response_model=TenantResponse,
    summary="Get tenant by ID",
    description="Retrieve a specific tenant by its ID"
)
async def get_tenant(
    tenant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a tenant by ID."""
    return await tenant_service.get_tenant(db=db, tenant_id=tenant_id)


@router.get(
    "/code/{tenant_code}",
    response_model=TenantResponse,
    summary="Get tenant by code",
    description="Retrieve a specific tenant by its tenant_code"
)
async def get_tenant_by_code(
    tenant_code: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a tenant by tenant_code."""
    return await tenant_service.get_tenant_by_code(db=db, tenant_code=tenant_code)


@router.put(
    "/{tenant_id}",
    response_model=TenantResponse,
    summary="Update tenant",
    description="Update an existing tenant's information"
)
async def update_tenant(
    *,
    tenant_id: int,
    tenant_in: TenantUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a tenant."""
    return await tenant_service.update_tenant(
        db=db,
        tenant_id=tenant_id,
        tenant_in=tenant_in
    )


@router.delete(
    "/{tenant_id}",
    response_model=TenantResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete tenant",
    description="Delete a tenant (soft delete by default)"
)
async def delete_tenant(
    tenant_id: int,
    soft_delete: bool = Query(True, description="Perform soft delete (default) or hard delete"),
    db: AsyncSession = Depends(get_db)
):
    """Delete a tenant."""
    return await tenant_service.delete_tenant(
        db=db,
        tenant_id=tenant_id,
        soft_delete=soft_delete
    )

