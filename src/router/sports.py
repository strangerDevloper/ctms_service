from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.service.sports import sport_service
from src.schema.sports import (
    SportCreate,
    SportUpdate,
    SportResponse,
    SportListResponse,
    SportQueryParams
)

router = APIRouter(
    prefix="/sport",
    tags=["Sports"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "",
    response_model=SportResponse,
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
    return await sport_service.create_sport(db=db, sport_in=sport_in)


@router.get(
    "",
    response_model=List[SportListResponse],
    summary="Get all sports",
    description="Retrieve a list of sports with pagination and filters. Returns only id, sport_code, sport_name, category, and status."
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
    """
    return await sport_service.get_sports(
        db=db,
        query_params=query_params
    )


@router.get(
    "/{sport_id}",
    response_model=SportResponse,
    summary="Get sport by ID",
    description="Retrieve a specific sport by its ID"
)
async def get_sport(
    sport_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a sport by ID."""
    return await sport_service.get_sport(db=db, sport_id=sport_id)


@router.get(
    "/code/{sport_code}",
    response_model=SportResponse,
    summary="Get sport by code",
    description="Retrieve a specific sport by its sport_code"
)
async def get_sport_by_code(
    sport_code: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a sport by sport_code."""
    return await sport_service.get_sport_by_code(db=db, sport_code=sport_code)


@router.put(
    "/{sport_id}",
    response_model=SportResponse,
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
    return await sport_service.update_sport(
        db=db,
        sport_id=sport_id,
        sport_in=sport_in
    )


@router.delete(
    "/{sport_id}",
    response_model=SportResponse,
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
    return await sport_service.delete_sport(
        db=db,
        sport_id=sport_id,
        soft_delete=soft_delete
    )

