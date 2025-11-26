from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.service.tenant import tenant_service
from src.schema.tenant import (
    TenantCreate,
    TenantUpdate,
    TenantResponse,
    TenantListResponse,
    TenantQueryParams
)

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
    response_model=List[TenantListResponse],
    summary="Get all tenants",
    description="Retrieve a list of tenants with pagination and filters. Returns only id, name, tenant_code, and status."
)
async def get_tenants(
    query_params: TenantQueryParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all tenants with pagination and filters.
    
    Query Parameters:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 100, max: 1000)
    - status: Filter by tenant status (optional)
    - search_id: Search by specific tenant ID (optional)
    - search: Search by tenant name or code - case-insensitive partial match (optional)
    - include_deleted: Include soft-deleted tenants (default: false)
    """
    return await tenant_service.get_tenants(
        db=db,
        query_params=query_params
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

