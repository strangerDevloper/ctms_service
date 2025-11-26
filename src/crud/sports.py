from typing import List, Optional
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from src.crud.base import CRUDBase
from src.models.sports import Sport, SportStatus, SportCategory
from src.schema.sports import SportCreate, SportUpdate, SportQueryParams


class CRUDSport(CRUDBase[Sport, SportCreate, SportUpdate]):
    """
    CRUD operations for Sport model.
    Extends base CRUD with sport-specific operations.
    """
    
    async def get_by_code(self, db: AsyncSession, *, sport_code: str) -> Optional[Sport]:
        """Get sport by sport_code."""
        result = await db.execute(
            select(Sport).filter(Sport.sport_code == sport_code)
        )
        return result.scalar_one_or_none()
    
    async def get_active_sports(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Sport]:
        """Get all active sports (not deleted and status is ACTIVE)."""
        query = (
            select(Sport)
            .filter(Sport.is_deleted == False)
            .filter(Sport.status == SportStatus.ACTIVE)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_status(
        self,
        db: AsyncSession,
        *,
        status: SportStatus,
        skip: int = 0,
        limit: int = 100
    ) -> List[Sport]:
        """Get sports by status."""
        query = (
            select(Sport)
            .filter(Sport.status == status)
            .filter(Sport.is_deleted == False)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_category(
        self,
        db: AsyncSession,
        *,
        category: SportCategory,
        skip: int = 0,
        limit: int = 100
    ) -> List[Sport]:
        """Get sports by category."""
        query = (
            select(Sport)
            .filter(Sport.category == category)
            .filter(Sport.is_deleted == False)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_multi(
        self,
        db: AsyncSession,
        *,
        query_params: SportQueryParams
    ) -> List[Sport]:
        """
        Get multiple sports with pagination and filters.
        
        Args:
            db: Database session
            query_params: Query parameters object containing filters and pagination
            
        Returns:
            List of Sport objects
        """
        query = select(Sport)
        
        # Filter by deleted status
        if not query_params.include_deleted:
            query = query.filter(Sport.is_deleted == False)
        
        # Filter by status
        if query_params.status is not None:
            query = query.filter(Sport.status == query_params.status)
        
        # Filter by category
        if query_params.category is not None:
            query = query.filter(Sport.category == query_params.category)
        
        # Filter by ID
        if query_params.search_id is not None:
            query = query.filter(Sport.id == query_params.search_id)
        
        # Search by name or code (case-insensitive partial match)
        if query_params.search:
            search_pattern = f"%{query_params.search}%"
            query = query.filter(
                or_(
                    Sport.sport_name.ilike(search_pattern),
                    Sport.sport_code.ilike(search_pattern)
                )
            )
        
        # Apply pagination
        query = query.offset(query_params.skip).limit(query_params.limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())


# Create an instance of CRUDSport
sport = CRUDSport(Sport)

