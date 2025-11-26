from typing import List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.crud.sports_config import sport_config as crud_sport_config
from src.models.sports_config import SportConfig
from src.schema.sports_config import (
    SportConfigCreate,
    SportConfigUpdate,
    SportConfigBulkCreate,
    SportConfigCreateWithoutSportId,
    SportConfigResponse,
    SportConfigListResponse
)


class SportConfigService:
    """
    Service layer for SportConfig operations.
    Contains business logic and validation.
    """
    
    @staticmethod
    async def get_config_by_sport_id(
        db: AsyncSession,
        sport_id: int
    ) -> List[SportConfigResponse]:
        """
        Get all configs for a specific sport.
        
        Args:
            db: Database session
            sport_id: Sport ID
            
        Returns:
            List of SportConfigResponse objects (empty list if sport has no configs or doesn't exist)
        """
        # Get configs
        configs = await crud_sport_config.get_by_sport_id(db=db, sport_id=sport_id)
        
        # Convert to response models
        return [SportConfigResponse.model_validate(config) for config in configs]
    
    @staticmethod
    async def create_config(
        db: AsyncSession,
        config_in: SportConfigCreate
    ) -> SportConfig:
        """
        Create a new sport config.
        Note: Sport validation is handled by database foreign key constraint.
        
        Args:
            db: Database session
            config_in: Config creation data
            
        Returns:
            Created SportConfig object
        """
        return await crud_sport_config.create(db=db, obj_in=config_in)
    
    @staticmethod
    async def create_config_bulk(
        db: AsyncSession,
        sport_id: int,
        bulk_create: SportConfigBulkCreate
    ) -> List[SportConfig]:
        """
        Create multiple sport configs in bulk for a specific sport.
        Note: Sport validation is handled by database foreign key constraint.
        
        Args:
            db: Database session
            sport_id: Sport ID from path parameter
            bulk_create: Bulk create data containing list of configs (without sport_id)
            
        Returns:
            List of created SportConfig objects
            
        Raises:
            HTTPException: If no configs provided
        """
        if not bulk_create.configs:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one config is required for bulk create"
            )
        
        # Convert configs without sport_id to configs with sport_id efficiently
        configs_with_sport_id = [
            SportConfigCreate(
                sport_id=sport_id,
                **(config.model_dump() if hasattr(config, 'model_dump') else config.dict())
            )
            for config in bulk_create.configs
        ]
        
        return await crud_sport_config.create_bulk(db=db, configs=configs_with_sport_id)
    
    @staticmethod
    async def update_config(
        db: AsyncSession,
        config_id: int,
        config_in: SportConfigUpdate
    ) -> SportConfig:
        """
        Update an existing sport config.
        
        Args:
            db: Database session
            config_id: Config ID
            config_in: Config update data
            
        Returns:
            Updated SportConfig object
            
        Raises:
            HTTPException: If config not found
        """
        config_obj = await crud_sport_config.get(db=db, id=config_id)
        if not config_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Config with ID {config_id} not found"
            )
        
        return await crud_sport_config.update(db=db, db_obj=config_obj, obj_in=config_in)
    
    @staticmethod
    async def get_config(
        db: AsyncSession,
        config_id: int
    ) -> SportConfig:
        """
        Get a config by ID.
        
        Args:
            db: Database session
            config_id: Config ID
            
        Returns:
            SportConfig object
            
        Raises:
            HTTPException: If config not found
        """
        config_obj = await crud_sport_config.get(db=db, id=config_id)
        if not config_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Config with ID {config_id} not found"
            )
        return config_obj
    
    @staticmethod
    async def delete_config(
        db: AsyncSession,
        config_id: int
    ) -> SportConfig:
        """
        Delete a config by ID.
        
        Args:
            db: Database session
            config_id: Config ID
            
        Returns:
            Deleted SportConfig object
            
        Raises:
            HTTPException: If config not found
        """
        config_obj = await crud_sport_config.delete(db=db, id=config_id)
        if not config_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Config with ID {config_id} not found"
            )
        return config_obj


# Create an instance of SportConfigService
sport_config_service = SportConfigService()

