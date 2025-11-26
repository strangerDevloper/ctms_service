from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.service.tenant import tenant_service
from src.utils.response import FormatResponse, StandardResponse, PaginatedData
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
    response_model=StandardResponse[TenantResponse],
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
    result = await tenant_service.create_tenant(db=db, tenant_in=tenant_in)
    return FormatResponse.created(
        data=result,
        msg="Tenant created successfully"
    )


@router.get(
    "",
    response_model=StandardResponse[PaginatedData[TenantListResponse]],
    summary="Get all tenants",
    description="Retrieve a list of tenants with pagination and filters. Returns only id, name, tenant_code, and status along with pagination metadata."
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
    
    Returns:
    - items: List of tenant objects
    - total_count: Total number of tenants matching the query
    - has_next_page: Boolean indicating if there are more results
    - skip: Number of items skipped
    - limit: Maximum number of items returned
    """
    result = await tenant_service.get_tenants(
        db=db,
        query_params=query_params
    )
    return FormatResponse.success(
        data=result,
        msg=f"Retrieved {len(result.items)} tenant(s) out of {result.total_count} total"
    )


@router.get(
    "/{tenant_id}",
    response_model=StandardResponse[TenantResponse],
    summary="Get tenant by ID",
    description="Retrieve a specific tenant by its ID"
)
async def get_tenant(
    tenant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a tenant by ID."""
    result = await tenant_service.get_tenant(db=db, tenant_id=tenant_id)
    return FormatResponse.success(
        data=result,
        msg="Tenant retrieved successfully"
    )


@router.get(
    "/code/{tenant_code}",
    response_model=StandardResponse[TenantResponse],
    summary="Get tenant by code",
    description="Retrieve a specific tenant by its tenant_code"
)
async def get_tenant_by_code(
    tenant_code: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a tenant by tenant_code."""
    result = await tenant_service.get_tenant_by_code(db=db, tenant_code=tenant_code)
    return FormatResponse.success(
        data=result,
        msg="Tenant retrieved successfully"
    )


@router.put(
    "/{tenant_id}",
    response_model=StandardResponse[TenantResponse],
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
    result = await tenant_service.update_tenant(
        db=db,
        tenant_id=tenant_id,
        tenant_in=tenant_in
    )
    return FormatResponse.success(
        data=result,
        msg="Tenant updated successfully"
    )


@router.delete(
    "/{tenant_id}",
    response_model=StandardResponse[TenantResponse],
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
    result = await tenant_service.delete_tenant(
        db=db,
        tenant_id=tenant_id,
        soft_delete=soft_delete
    )
    delete_type = "soft deleted" if soft_delete else "deleted"
    return FormatResponse.success(
        data=result,
        msg=f"Tenant {delete_type} successfully"
    )

