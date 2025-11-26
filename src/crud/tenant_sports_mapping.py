from typing import List, Optional, Tuple
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from src.crud.base import CRUDBase
from src.models.tenant_sports_mapping import TenantSportsMapping, MappingStatus
from src.schema.tenant_sports_mapping import (
    TenantSportsMappingCreate,
    TenantSportsMappingUpdate
)


class CRUDTenantSportsMapping(CRUDBase[TenantSportsMapping, TenantSportsMappingCreate, TenantSportsMappingUpdate]):
    """
    CRUD operations for TenantSportsMapping model.
    Extends base CRUD with mapping-specific operations.
    """
    
    async def get_by_tenant_and_sport(
        self,
        db: AsyncSession,
        *,
        tenant_id: int,
        sport_id: int
    ) -> Optional[TenantSportsMapping]:
        """Get mapping by tenant_id and sport_id."""
        result = await db.execute(
            select(TenantSportsMapping).filter(
                and_(
                    TenantSportsMapping.tenant_id == tenant_id,
                    TenantSportsMapping.sport_id == sport_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_tenant(
        self,
        db: AsyncSession,
        *,
        tenant_id: int,
        status: Optional[MappingStatus] = None
    ) -> List[TenantSportsMapping]:
        """Get all mappings for a specific tenant."""
        query = select(TenantSportsMapping).filter(
            TenantSportsMapping.tenant_id == tenant_id
        )
        
        if status is not None:
            query = query.filter(TenantSportsMapping.status == status)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_sport(
        self,
        db: AsyncSession,
        *,
        sport_id: int,
        status: Optional[MappingStatus] = None
    ) -> List[TenantSportsMapping]:
        """Get all mappings for a specific sport."""
        query = select(TenantSportsMapping).filter(
            TenantSportsMapping.sport_id == sport_id
        )
        
        if status is not None:
            query = query.filter(TenantSportsMapping.status == status)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def exists(
        self,
        db: AsyncSession,
        *,
        tenant_id: int,
        sport_id: int
    ) -> bool:
        """Check if a mapping exists for tenant_id and sport_id."""
        mapping = await self.get_by_tenant_and_sport(
            db=db,
            tenant_id=tenant_id,
            sport_id=sport_id
        )
        return mapping is not None
    
    async def count_existing_mappings(
        self,
        db: AsyncSession,
        *,
        tenant_id: int,
        sport_ids: List[int]
    ) -> int:
        """
        Count existing mappings for a tenant and list of sport IDs.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            sport_ids: List of sport IDs to check
            
        Returns:
            Count of existing mappings
        """
        if not sport_ids:
            return 0
        
        query = select(func.count(TenantSportsMapping.id)).filter(
            and_(
                TenantSportsMapping.tenant_id == tenant_id,
                TenantSportsMapping.sport_id.in_(sport_ids)
            )
        )
        result = await db.execute(query)
        return result.scalar_one() or 0
    
    async def bulk_create(
        self,
        db: AsyncSession,
        *,
        mappings: List[TenantSportsMappingCreate]
    ) -> List[TenantSportsMapping]:
        """
        Create multiple mappings in a single operation.
        
        Args:
            db: Database session
            mappings: List of mapping data to create
            
        Returns:
            List of created TenantSportsMapping objects
        """
        if not mappings:
            return []
        
        # Create mapping objects from Pydantic models
        db_objs = []
        for mapping in mappings:
            # Convert Pydantic model to dict
            if hasattr(mapping, 'model_dump'):
                mapping_data = mapping.model_dump()
            else:
                mapping_data = mapping.dict()
            
            # Create SQLAlchemy model instance
            db_obj = TenantSportsMapping(**jsonable_encoder(mapping_data))
            db_objs.append(db_obj)
        
        # Add all to session
        db.add_all(db_objs)
        await db.commit()
        
        # Refresh all objects
        for db_obj in db_objs:
            await db.refresh(db_obj)
        
        return db_objs


# Create an instance of CRUDTenantSportsMapping
tenant_sports_mapping = CRUDTenantSportsMapping(TenantSportsMapping)

