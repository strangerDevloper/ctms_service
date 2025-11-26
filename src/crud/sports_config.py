from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.crud.base import CRUDBase
from src.models.sports_config import SportConfig
from src.schema.sports_config import SportConfigCreate, SportConfigUpdate


class CRUDSportConfig(CRUDBase[SportConfig, SportConfigCreate, SportConfigUpdate]):
    """
    CRUD operations for SportConfig model.
    Extends base CRUD with sport config-specific operations.
    """
    
    async def get_by_sport_id(
        self,
        db: AsyncSession,
        *,
        sport_id: int
    ) -> List[SportConfig]:
        """Get all configs for a specific sport."""
        query = select(SportConfig).filter(SportConfig.sport_id == sport_id)
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def create_bulk(
        self,
        db: AsyncSession,
        *,
        configs: List[SportConfigCreate]
    ) -> List[SportConfig]:
        """
        Create multiple sport configs in bulk.
        
        Args:
            db: Database session
            configs: List of config creation data
            
        Returns:
            List of created SportConfig objects
        """
        # Create all objects efficiently
        db_objs = [
            SportConfig(**(
                config_in.model_dump() if hasattr(config_in, 'model_dump') else config_in.dict()
            ))
            for config_in in configs
        ]
        
        db.add_all(db_objs)
        await db.commit()
        
        # Refresh all objects (necessary to get generated IDs and timestamps)
        for db_obj in db_objs:
            await db.refresh(db_obj)
        
        return db_objs


# Create an instance of CRUDSportConfig
sport_config = CRUDSportConfig(SportConfig)

