from typing import List, Optional, Tuple
from sqlalchemy import select, or_, func
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
    
    async def validate_sports_exist(
        self,
        db: AsyncSession,
        *,
        sport_ids: List[int]
    ) -> Tuple[List[int], List[int]]:
        """
        Validate that multiple sports exist and are not deleted.
        
        Args:
            db: Database session
            sport_ids: List of sport IDs to validate
            
        Returns:
            Tuple of (valid_sport_ids, invalid_sport_ids)
            - valid_sport_ids: List of sport IDs that exist and are not deleted
            - invalid_sport_ids: List of sport IDs that don't exist or are deleted
        """
        if not sport_ids:
            return [], []
        
        # Query all sports at once
        query = select(Sport.id, Sport.is_deleted).filter(Sport.id.in_(sport_ids))
        result = await db.execute(query)
        sport_rows = result.all()
        
        # Create sets for comparison
        valid_sport_ids = {row[0] for row in sport_rows if not row[1]}  # Not deleted
        all_found_ids = {row[0] for row in sport_rows}
        
        # Find invalid IDs (not found or deleted)
        invalid_sport_ids = []
        for sport_id in sport_ids:
            if sport_id not in all_found_ids:
                invalid_sport_ids.append(sport_id)
            elif sport_id not in valid_sport_ids:
                invalid_sport_ids.append(sport_id)
        
        return list(valid_sport_ids), invalid_sport_ids
    
    async def get_multi(
        self,
        db: AsyncSession,
        *,
        query_params: SportQueryParams
    ) -> Tuple[List[Sport], int]:
        """
        Get multiple sports with pagination and filters.
        
        Args:
            db: Database session
            query_params: Query parameters object containing filters and pagination
            
        Returns:
            Tuple of (List of Sport objects, total count)
        """
        # Build base query for filtering
        base_query = select(Sport)
        
        # Filter by deleted status
        if not query_params.include_deleted:
            base_query = base_query.filter(Sport.is_deleted == False)
        
        # Filter by status
        if query_params.status is not None:
            base_query = base_query.filter(Sport.status == query_params.status)
        
        # Filter by category
        if query_params.category is not None:
            base_query = base_query.filter(Sport.category == query_params.category)
        
        # Filter by ID
        if query_params.search_id is not None:
            base_query = base_query.filter(Sport.id == query_params.search_id)
        
        # Search by name or code (case-insensitive partial match)
        if query_params.search:
            search_pattern = f"%{query_params.search}%"
            base_query = base_query.filter(
                or_(
                    Sport.sport_name.ilike(search_pattern),
                    Sport.sport_code.ilike(search_pattern)
                )
            )
        
        # Get total count (apply same filters but without pagination)
        count_query = select(func.count(Sport.id))
        
        # Apply same filters as base_query
        if not query_params.include_deleted:
            count_query = count_query.filter(Sport.is_deleted == False)
        
        if query_params.status is not None:
            count_query = count_query.filter(Sport.status == query_params.status)
        
        if query_params.category is not None:
            count_query = count_query.filter(Sport.category == query_params.category)
        
        if query_params.search_id is not None:
            count_query = count_query.filter(Sport.id == query_params.search_id)
        
        if query_params.search:
            search_pattern = f"%{query_params.search}%"
            count_query = count_query.filter(
                or_(
                    Sport.sport_name.ilike(search_pattern),
                    Sport.sport_code.ilike(search_pattern)
                )
            )
        
        count_result = await db.execute(count_query)
        total_count = count_result.scalar_one()
        
        # Apply pagination to get items
        query = base_query.offset(query_params.skip).limit(query_params.limit)
        result = await db.execute(query)
        items = list(result.scalars().all())
        
        return items, total_count


# Create an instance of CRUDSport
sport = CRUDSport(Sport)

