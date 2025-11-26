from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.service.sports import sport_service
from src.service.sports_config import sport_config_service
from src.utils.response import FormatResponse, StandardResponse, PaginatedData
from src.schema.sports import (
    SportCreate,
    SportUpdate,
    SportResponse,
    SportListResponse,
    SportQueryParams
)
from src.schema.sports_config import (
    SportConfigUpdate,
    SportConfigBulkCreate,
    SportConfigResponse,
    SportConfigListResponse
)

router = APIRouter(
    prefix="/sport",
    tags=["Sports"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "",
    response_model=StandardResponse[SportResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new sport",
    description="Create a new sport with the provided information"
)
async def create_sport(
    *,
    db: AsyncSession = Depends(get_db),
    sport_in: SportCreate
):
    """Create a new sport."""
    result = await sport_service.create_sport(db=db, sport_in=sport_in)
    return FormatResponse.created(
        data=result,
        msg="Sport created successfully"
    )


@router.get(
    "",
    response_model=StandardResponse[PaginatedData[SportListResponse]],
    summary="Get all sports",
    description="Retrieve a list of sports with pagination and filters. Returns only id, sport_code, sport_name, category, and status along with pagination metadata."
)
async def get_sports(
    query_params: SportQueryParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all sports with pagination and filters.
    
    Query Parameters:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 100, max: 1000)
    - status: Filter by sport status (optional)
    - category: Filter by sport category (optional)
    - search_id: Search by specific sport ID (optional)
    - search: Search by sport name or code - case-insensitive partial match (optional)
    - include_deleted: Include soft-deleted sports (default: false)
    
    Returns:
    - items: List of sport objects
    - total_count: Total number of sports matching the query
    - has_next_page: Boolean indicating if there are more results
    - skip: Number of items skipped
    - limit: Maximum number of items returned
    """
    result = await sport_service.get_sports(
        db=db,
        query_params=query_params
    )
    return FormatResponse.success(
        data=result,
        msg=f"Retrieved {len(result.items)} sport(s) out of {result.total_count} total"
    )


@router.get(
    "/{sport_id}/config",
    response_model=StandardResponse[SportConfigListResponse],
    summary="Get configs by sport ID",
    description="Retrieve all configs for a specific sport"
)
async def get_configs_by_sport_id(
    sport_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all configs for a specific sport."""
    configs = await sport_config_service.get_config_by_sport_id(db=db, sport_id=sport_id)
    return FormatResponse.success(
        data=SportConfigListResponse(
            items=configs,
            total_count=len(configs)
        ),
        msg=f"Retrieved {len(configs)} config(s) for sport ID {sport_id}"
    )


@router.get(
    "/{sport_id}",
    response_model=StandardResponse[SportResponse],
    summary="Get sport by ID",
    description="Retrieve a specific sport by its ID. Optionally include configs via query parameter."
)
async def get_sport(
    sport_id: int,
    include_configs: bool = Query(False, description="Include sport configs in the response"),
    db: AsyncSession = Depends(get_db)
):
    """Get a sport by ID."""
    result = await sport_service.get_sport(db=db, sport_id=sport_id, include_configs=include_configs)
    return FormatResponse.success(
        data=result,
        msg="Sport retrieved successfully"
    )


@router.get(
    "/code/{sport_code}",
    response_model=StandardResponse[SportResponse],
    summary="Get sport by code",
    description="Retrieve a specific sport by its sport_code"
)
async def get_sport_by_code(
    sport_code: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a sport by sport_code."""
    result = await sport_service.get_sport_by_code(db=db, sport_code=sport_code)
    return FormatResponse.success(
        data=result,
        msg="Sport retrieved successfully"
    )


@router.put(
    "/{sport_id}",
    response_model=StandardResponse[SportResponse],
    summary="Update sport",
    description="Update an existing sport's information"
)
async def update_sport(
    *,
    sport_id: int,
    sport_in: SportUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a sport."""
    result = await sport_service.update_sport(
        db=db,
        sport_id=sport_id,
        sport_in=sport_in
    )
    return FormatResponse.success(
        data=result,
        msg="Sport updated successfully"
    )


@router.delete(
    "/{sport_id}",
    response_model=StandardResponse[SportResponse],
    status_code=status.HTTP_200_OK,
    summary="Delete sport",
    description="Delete a sport (soft delete by default)"
)
async def delete_sport(
    sport_id: int,
    soft_delete: bool = Query(True, description="Perform soft delete (default) or hard delete"),
    db: AsyncSession = Depends(get_db)
):
    """Delete a sport."""
    result = await sport_service.delete_sport(
        db=db,
        sport_id=sport_id,
        soft_delete=soft_delete
    )
    delete_type = "soft deleted" if soft_delete else "deleted"
    return FormatResponse.success(
        data=result,
        msg=f"Sport {delete_type} successfully"
    )


# Sport Config Endpoints

@router.post(
    "/{sport_id}/config",
    response_model=StandardResponse[List[SportConfigResponse]],
    status_code=status.HTTP_201_CREATED,
    summary="Create sport config(s) - Bulk",
    description="Create multiple sport configs in bulk for a specific sport. Sport ID comes from path parameter."
)
async def create_sport_config_bulk(
    *,
    sport_id: int,
    db: AsyncSession = Depends(get_db),
    bulk_create: SportConfigBulkCreate
):
    """Create sport config(s) in bulk for a specific sport."""
    result = await sport_config_service.create_config_bulk(
        db=db,
        sport_id=sport_id,
        bulk_create=bulk_create
    )
    return FormatResponse.created(
        data=[SportConfigResponse.model_validate(config) for config in result],
        msg=f"Created {len(result)} config(s) successfully"
    )


@router.put(
    "/config/{config_id}",
    response_model=StandardResponse[SportConfigResponse],
    summary="Update sport config",
    description="Update an existing sport config"
)
async def update_sport_config(
    *,
    config_id: int,
    config_in: SportConfigUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a sport config."""
    result = await sport_config_service.update_config(
        db=db,
        config_id=config_id,
        config_in=config_in
    )
    return FormatResponse.success(
        data=SportConfigResponse.model_validate(result),
        msg="Config updated successfully"
    )


@router.delete(
    "/config/{config_id}",
    response_model=StandardResponse[SportConfigResponse],
    status_code=status.HTTP_200_OK,
    summary="Delete sport config",
    description="Delete a sport config by ID"
)
async def delete_sport_config(
    config_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a sport config."""
    result = await sport_config_service.delete_config(
        db=db,
        config_id=config_id
    )
    return FormatResponse.success(
        data=SportConfigResponse.model_validate(result),
        msg="Config deleted successfully"
    )



