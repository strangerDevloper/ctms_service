from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.crud.sports import sport as crud_sport
from src.models.sports import Sport, SportStatus, SportCategory
from src.schema.sports import SportCreate, SportUpdate, SportListResponse, SportQueryParams
from src.utils.response import PaginatedData


class SportService:
    """
    Service layer for Sport operations.
    Contains business logic and validation.
    """
    
    @staticmethod
    async def get_sport(db: AsyncSession, sport_id: int) -> Sport:
        """
        Get a sport by ID.
        
        Args:
            db: Database session
            sport_id: Sport ID
            
        Returns:
            Sport object
            
        Raises:
            HTTPException: If sport not found
        """
        sport_obj = await crud_sport.get(db=db, id=sport_id)
        if not sport_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sport with ID {sport_id} not found"
            )
        if sport_obj.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sport with ID {sport_id} has been deleted"
            )
        return sport_obj
    
    @staticmethod
    async def get_sports(
        db: AsyncSession,
        query_params: SportQueryParams
    ) -> PaginatedData[SportListResponse]:
        """
        Get multiple sports with pagination and filters.
        
        Args:
            db: Database session
            query_params: Query parameters object containing filters and pagination
            
        Returns:
            PaginatedData containing list of SportListResponse objects, total count, and pagination info
        """
        items, total_count = await crud_sport.get_multi(
            db=db,
            query_params=query_params
        )
        
        # Convert SQLAlchemy models to Pydantic models
        sport_list = [SportListResponse.model_validate(sport) for sport in items]
        
        # Calculate has_next_page
        has_next_page = (query_params.skip + query_params.limit) < total_count
        
        return PaginatedData(
            items=sport_list,
            total_count=total_count,
            has_next_page=has_next_page,
            skip=query_params.skip,
            limit=query_params.limit
        )
    
    @staticmethod
    async def get_sport_by_code(db: AsyncSession, sport_code: str) -> Sport:
        """
        Get a sport by sport_code.
        
        Args:
            db: Database session
            sport_code: Sport code
            
        Returns:
            Sport object
            
        Raises:
            HTTPException: If sport not found
        """
        sport_obj = await crud_sport.get_by_code(db=db, sport_code=sport_code)
        if not sport_obj or sport_obj.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sport with code '{sport_code}' not found"
            )
        return sport_obj
    
    @staticmethod
    async def create_sport(db: AsyncSession, sport_in: SportCreate) -> Sport:
        """
        Create a new sport.
        
        Args:
            db: Database session
            sport_in: Sport creation data
            
        Returns:
            Created Sport object
            
        Raises:
            HTTPException: If sport_code already exists
        """
        # Check if sport_code already exists
        existing_sport = await crud_sport.get_by_code(db=db, sport_code=sport_in.sport_code)
        if existing_sport:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Sport with code '{sport_in.sport_code}' already exists"
            )
        
        return await crud_sport.create(db=db, obj_in=sport_in)
    
    @staticmethod
    async def update_sport(
        db: AsyncSession,
        sport_id: int,
        sport_in: SportUpdate
    ) -> Sport:
        """
        Update an existing sport.
        
        Args:
            db: Database session
            sport_id: Sport ID
            sport_in: Sport update data
            
        Returns:
            Updated Sport object
            
        Raises:
            HTTPException: If sport not found or sport_code conflict
        """
        sport_obj = await SportService.get_sport(db=db, sport_id=sport_id)
        
        # Check if sport_code is being updated and conflicts with existing
        if sport_in.sport_code and sport_in.sport_code != sport_obj.sport_code:
            existing_sport = await crud_sport.get_by_code(db=db, sport_code=sport_in.sport_code)
            if existing_sport and existing_sport.id != sport_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Sport with code '{sport_in.sport_code}' already exists"
                )
        
        return await crud_sport.update(db=db, db_obj=sport_obj, obj_in=sport_in)
    
    @staticmethod
    async def delete_sport(db: AsyncSession, sport_id: int, soft_delete: bool = True) -> Sport:
        """
        Delete a sport (soft delete by default).
        
        Args:
            db: Database session
            sport_id: Sport ID
            soft_delete: If True, perform soft delete, else hard delete
            
        Returns:
            Deleted Sport object
            
        Raises:
            HTTPException: If sport not found
        """
        sport_obj = await SportService.get_sport(db=db, sport_id=sport_id)
        
        if soft_delete:
            return await crud_sport.soft_delete(db=db, id=sport_id)
        else:
            return await crud_sport.delete(db=db, id=sport_id)
    
    @staticmethod
    async def get_active_sports(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[Sport]:
        """
        Get all active sports.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of active Sport objects
        """
        return await crud_sport.get_active_sports(db=db, skip=skip, limit=limit)
    
    @staticmethod
    async def get_sports_by_status(
        db: AsyncSession,
        status: SportStatus,
        skip: int = 0,
        limit: int = 100
    ) -> List[Sport]:
        """
        Get sports by status.
        
        Args:
            db: Database session
            status: Sport status
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of Sport objects with specified status
        """
        return await crud_sport.get_by_status(db=db, status=status, skip=skip, limit=limit)
    
    @staticmethod
    async def get_sports_by_category(
        db: AsyncSession,
        category: SportCategory,
        skip: int = 0,
        limit: int = 100
    ) -> List[Sport]:
        """
        Get sports by category.
        
        Args:
            db: Database session
            category: Sport category
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of Sport objects with specified category
        """
        return await crud_sport.get_by_category(db=db, category=category, skip=skip, limit=limit)


# Create an instance of SportService
sport_service = SportService()

