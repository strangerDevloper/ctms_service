from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base CRUD class with default async CRUD operations.
    
    This class provides common database operations that can be inherited
    by specific CRUD classes for each model.
    
    Generic Types:
        ModelType: SQLAlchemy model class
        CreateSchemaType: Pydantic schema for creation
        UpdateSchemaType: Pydantic schema for update
    """
    
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        
        Args:
            model: A SQLAlchemy model class
        """
        self.model = model
    
    async def get(self, db: AsyncSession, *, id: Any) -> Optional[ModelType]:
        """Get a single record by ID."""
        result = await db.execute(select(self.model).filter(self.model.id == id))
        return result.scalar_one_or_none()
    
    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """
        Get multiple records with pagination and optional filters.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Dictionary of filters to apply
        """
        query = select(self.model)
        
        # Apply filters if provided
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record."""
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Update an existing record."""
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            # Pydantic v2 uses model_dump instead of dict
            if hasattr(obj_in, 'model_dump'):
                update_data = obj_in.model_dump(exclude_unset=True)
            else:
                update_data = obj_in.dict(exclude_unset=True)
        
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def delete(self, db: AsyncSession, *, id: int) -> Optional[ModelType]:
        """Delete a record by ID."""
        result = await db.execute(select(self.model).filter(self.model.id == id))
        obj = result.scalar_one_or_none()
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj
    
    async def soft_delete(self, db: AsyncSession, *, id: int) -> Optional[ModelType]:
        """
        Soft delete a record by setting is_deleted flag to True.
        Only works if model has is_deleted attribute.
        """
        if not hasattr(self.model, 'is_deleted'):
            raise AttributeError(f"{self.model.__name__} does not have 'is_deleted' attribute")
        
        result = await db.execute(select(self.model).filter(self.model.id == id))
        obj = result.scalar_one_or_none()
        if obj:
            obj.is_deleted = True
            db.add(obj)
            await db.commit()
            await db.refresh(obj)
        return obj
    
    async def get_by_field(
        self,
        db: AsyncSession,
        *,
        field_name: str,
        field_value: Any
    ) -> Optional[ModelType]:
        """Get a record by a specific field value."""
        if not hasattr(self.model, field_name):
            raise AttributeError(f"{self.model.__name__} does not have '{field_name}' attribute")
        
        result = await db.execute(
            select(self.model).filter(getattr(self.model, field_name) == field_value)
        )
        return result.scalar_one_or_none()
    
    async def exists(self, db: AsyncSession, *, id: int) -> bool:
        """Check if a record exists by ID."""
        result = await db.execute(select(self.model).filter(self.model.id == id))
        return result.scalar_one_or_none() is not None

