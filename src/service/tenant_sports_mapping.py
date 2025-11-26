from typing import List, Optional, Tuple
import asyncio
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.crud.tenant_sports_mapping import tenant_sports_mapping as crud_mapping
from src.crud.tenant import tenant as crud_tenant
from src.crud.sports import sport as crud_sport
from src.models.tenant_sports_mapping import TenantSportsMapping, MappingStatus
from src.models.tenants import Tenant
from src.models.sports import Sport
from src.schema.tenant_sports_mapping import (
    TenantSportsMappingCreate,
    TenantSportsMappingUpdate,
    RegisterSportRequest,
    BulkRegisterSportRequest,
    RegisterSportItem
)


class TenantSportsMappingService:
    """
    Service layer for TenantSportsMapping operations.
    Contains business logic and validation.
    """
    
    @staticmethod
    async def validate_tenant_exists(db: AsyncSession, tenant_id: int) -> None:
        """Validate that tenant exists and is not deleted."""
        tenant = await crud_tenant.get(db=db, id=tenant_id)
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tenant with ID {tenant_id} not found"
            )
        if tenant.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tenant with ID {tenant_id} has been deleted"
            )
    
    @staticmethod
    async def validate_sport_exists(db: AsyncSession, sport_id: int) -> None:
        """Validate that sport exists and is not deleted."""
        sport = await crud_sport.get(db=db, id=sport_id)
        if not sport:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sport with ID {sport_id} not found"
            )
        if sport.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sport with ID {sport_id} has been deleted"
            )
    
    @staticmethod
    async def validate_tenant_and_sport(
        db: AsyncSession,
        tenant_id: int,
        sport_id: int
    ) -> Tuple[int, int]:
        """
        Validate that both tenant and sport exist and are not deleted.
        Executes both queries in parallel for better performance.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            sport_id: Sport ID
            
        Returns:
            Tuple of (Tenant, Sport) objects
            
        Raises:
            HTTPException: If tenant or sport not found or deleted
        """
        # Execute both queries in parallel for better performance
        # Pass coroutines directly to asyncio.gather
        tenant_result, sport_result = await asyncio.gather(
            db.execute(select(Tenant.id, Tenant.is_deleted).filter(Tenant.id == tenant_id)),
            db.execute(select(Sport.id, Sport.is_deleted).filter(Sport.id == sport_id))
        )
        
        tenant_id, tenant_is_deleted = tenant_result.scalar_one_or_none()
        sport_id, sport_is_deleted = sport_result.scalar_one_or_none()
        
        # Validate tenant
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tenant with ID {tenant_id} not found"
            )
        if tenant_is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tenant with ID {tenant_id} has been deleted"
            )
        
        # Validate sport
        if not sport_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sport with ID {sport_id} not found"
            )
        if sport_is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sport with ID {sport_id} has been deleted"
            )
        
        return tenant_id, sport_id
    
    @staticmethod
    async def register_sport(
        db: AsyncSession,
        tenant_id: int,
        request: RegisterSportRequest
    ) -> TenantSportsMapping:
        """
        Register a sport under a tenant.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            request: Register sport request data
            
        Returns:
            Created TenantSportsMapping object
            
        Raises:
            HTTPException: If tenant or sport not found, or mapping already exists
        """
        # Optimized validation: Check mapping existence first (early exit if exists)
        # Then validate tenant and sport in a single optimized call
        existing_mapping = await crud_mapping.get_by_tenant_and_sport(
            db=db,
            tenant_id=tenant_id,
            sport_id=request.sport_id
        )
        if existing_mapping:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Sport with ID {request.sport_id} is already registered for tenant {tenant_id}"
            )
        
        # Validate tenant and sport exist (optimized: single method call)
        await TenantSportsMappingService.validate_tenant_and_sport(
            db=db,
            tenant_id=tenant_id,
            sport_id=request.sport_id
        )
        
        # Create mapping
        mapping_data = TenantSportsMappingCreate(
            tenant_id=tenant_id,
            sport_id=request.sport_id,
            status=request.status or MappingStatus.ACTIVE,
            desciption=request.desciption,
            created_by=request.created_by
        )
        
        return await crud_mapping.create(db=db, obj_in=mapping_data)
    
    @staticmethod
    async def bulk_register_sports(
        db: AsyncSession,
        tenant_id: int,
        request: BulkRegisterSportRequest
    ) -> List[TenantSportsMapping]:
        """
        Register multiple sports under a tenant in a single operation.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            request: Bulk register sports request data
            
        Returns:
            List of created TenantSportsMapping objects
            
        Raises:
            HTTPException: If tenant not found, any sport not found, or any mapping already exists
        """
        if not request.sports:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one sport must be provided"
            )
        
        # Extract unique sport IDs
        sport_ids = list(set([sport.sport_id for sport in request.sports]))
        
        # Validate tenant exists
        tenant_exists = await crud_tenant.validate_exists(db=db, tenant_id=tenant_id)
        if not tenant_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tenant with ID {tenant_id} not found or has been deleted"
            )
        
        # Validate all sports exist using CRUD method (single query with IN clause)
        valid_sport_ids, invalid_sport_ids = await crud_sport.validate_sports_exist(
            db=db,
            sport_ids=sport_ids
        )
        
        # Validate all sports exist (count comparison)
        if len(valid_sport_ids) != len(sport_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more sports not found or have been deleted"
            )
        
        # Check for existing mappings using count-based query
        existing_count = await crud_mapping.count_existing_mappings(
            db=db,
            tenant_id=tenant_id,
            sport_ids=sport_ids
        )
        
        if existing_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more sports are already registered for this tenant"
            )
        
        # Prepare bulk create data
        mapping_data_list = [
            TenantSportsMappingCreate(
                tenant_id=tenant_id,
                sport_id=sport.sport_id,
                status=MappingStatus.ACTIVE,
                desciption=sport.desciption,
                created_by=request.created_by or 1
            )
            for sport in request.sports
        ]
        
        # Bulk create all mappings
        created_mappings = await crud_mapping.bulk_create(
            db=db,
            mappings=mapping_data_list
        )
        
        return created_mappings
    
    @staticmethod
    async def get_mapping(
        db: AsyncSession,
        mapping_id: int
    ) -> TenantSportsMapping:
        """
        Get a mapping by ID.
        
        Args:
            db: Database session
            mapping_id: Mapping ID
            
        Returns:
            TenantSportsMapping object
            
        Raises:
            HTTPException: If mapping not found
        """
        mapping = await crud_mapping.get(db=db, id=mapping_id)
        if not mapping:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mapping with ID {mapping_id} not found"
            )
        return mapping
    
    @staticmethod
    async def get_mappings_by_tenant(
        db: AsyncSession,
        tenant_id: int,
        status: Optional[MappingStatus] = None
    ) -> List[TenantSportsMapping]:
        """
        Get all mappings for a tenant.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            status: Optional status filter
            
        Returns:
            List of TenantSportsMapping objects
        """
        # Validate tenant exists
        await TenantSportsMappingService.validate_tenant_exists(db=db, tenant_id=tenant_id)
        
        return await crud_mapping.get_by_tenant(
            db=db,
            tenant_id=tenant_id,
            status=status
        )
    
    @staticmethod
    async def update_mapping(
        db: AsyncSession,
        mapping_id: int,
        mapping_in: TenantSportsMappingUpdate
    ) -> TenantSportsMapping:
        """
        Update a mapping (can be used to unregister by setting status to INACTIVE).
        
        Args:
            db: Database session
            mapping_id: Mapping ID
            mapping_in: Update data
            
        Returns:
            Updated TenantSportsMapping object
            
        Raises:
            HTTPException: If mapping not found
        """
        mapping = await TenantSportsMappingService.get_mapping(
            db=db,
            mapping_id=mapping_id
        )
        
        return await crud_mapping.update(db=db, db_obj=mapping, obj_in=mapping_in)
    
    @staticmethod
    async def update_mapping_by_tenant_sport(
        db: AsyncSession,
        tenant_id: int,
        sport_id: int,
        mapping_in: TenantSportsMappingUpdate
    ) -> TenantSportsMapping:
        """
        Update a mapping by tenant_id and sport_id.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            sport_id: Sport ID
            mapping_in: Update data
            
        Returns:
            Updated TenantSportsMapping object
            
        Raises:
            HTTPException: If mapping not found
        """
        mapping = await crud_mapping.get_by_tenant_and_sport(
            db=db,
            tenant_id=tenant_id,
            sport_id=sport_id
        )
        
        if not mapping:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mapping for tenant {tenant_id} and sport {sport_id} not found"
            )
        
        return await crud_mapping.update(db=db, db_obj=mapping, obj_in=mapping_in)


# Create an instance of TenantSportsMappingService
tenant_sports_mapping_service = TenantSportsMappingService()

