# Quick Template for Creating a New Model

Copy and adapt these templates to create a new model quickly.

## 1. Model File: `src/models/your_model.py`

```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from src.database import Base

class YourModel(Base):
    __tablename__ = "your_table"
    __table_args__ = {"schema": "public"}
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=False), server_default=func.current_timestamp(), nullable=False)
    updated_at = Column(DateTime(timezone=False), server_default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
```

## 2. Schema File: `src/schema/your_model.py`

```python
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from src.models.your_model import YourModelStatus  # if needed

class YourModelBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)

class YourModelCreate(YourModelBase):
    pass

class YourModelUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    
class YourModelResponse(YourModelBase):
    id: int
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    
    class Config:
        from_attributes = True

class YourModelListResponse(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True

class YourModelQueryParams(BaseModel):
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=1000)
    search: Optional[str] = Field(default=None)
    
    class Config:
        from_attributes = True
```

## 3. CRUD File: `src/crud/your_model.py`

```python
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.crud.base import CRUDBase
from src.models.your_model import YourModel
from src.schema.your_model import YourModelCreate, YourModelUpdate, YourModelQueryParams

class CRUDYourModel(CRUDBase[YourModel, YourModelCreate, YourModelUpdate]):
    async def get_multi(
        self,
        db: AsyncSession,
        *,
        query_params: YourModelQueryParams
    ) -> List[YourModel]:
        query = select(YourModel)
        
        if not query_params.include_deleted:
            query = query.filter(YourModel.is_deleted == False)
        
        if query_params.search:
            search_pattern = f"%{query_params.search}%"
            query = query.filter(YourModel.name.ilike(search_pattern))
        
        query = query.offset(query_params.skip).limit(query_params.limit)
        result = await db.execute(query)
        return list(result.scalars().all())

your_model = CRUDYourModel(YourModel)
```

## 4. Service File: `src/service/your_model.py`

```python
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.crud.your_model import your_model as crud_your_model
from src.models.your_model import YourModel
from src.schema.your_model import YourModelCreate, YourModelUpdate, YourModelQueryParams

class YourModelService:
    @staticmethod
    async def get_your_model(db: AsyncSession, your_model_id: int) -> YourModel:
        obj = await crud_your_model.get(db=db, id=your_model_id)
        if not obj:
            raise HTTPException(status_code=404, detail=f"YourModel {your_model_id} not found")
        return obj
    
    @staticmethod
    async def get_your_models(db: AsyncSession, query_params: YourModelQueryParams) -> List[YourModel]:
        return await crud_your_model.get_multi(db=db, query_params=query_params)
    
    @staticmethod
    async def create_your_model(db: AsyncSession, obj_in: YourModelCreate) -> YourModel:
        return await crud_your_model.create(db=db, obj_in=obj_in)
    
    @staticmethod
    async def update_your_model(db: AsyncSession, your_model_id: int, obj_in: YourModelUpdate) -> YourModel:
        obj = await YourModelService.get_your_model(db=db, your_model_id=your_model_id)
        return await crud_your_model.update(db=db, db_obj=obj, obj_in=obj_in)
    
    @staticmethod
    async def delete_your_model(db: AsyncSession, your_model_id: int, soft_delete: bool = True) -> YourModel:
        obj = await YourModelService.get_your_model(db=db, your_model_id=your_model_id)
        if soft_delete:
            return await crud_your_model.soft_delete(db=db, id=your_model_id)
        return await crud_your_model.delete(db=db, id=your_model_id)

your_model_service = YourModelService()
```

## 5. Router File: `src/router/your_model.py`

```python
from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.service.your_model import your_model_service
from src.schema.your_model import YourModelCreate, YourModelUpdate, YourModelResponse, YourModelListResponse, YourModelQueryParams

router = APIRouter(prefix="/your-model", tags=["Your Models"])

@router.post("", response_model=YourModelResponse, status_code=status.HTTP_201_CREATED)
async def create_your_model(*, db: AsyncSession = Depends(get_db), obj_in: YourModelCreate):
    return await your_model_service.create_your_model(db=db, obj_in=obj_in)

@router.get("", response_model=List[YourModelListResponse])
async def get_your_models(query_params: YourModelQueryParams = Depends(), db: AsyncSession = Depends(get_db)):
    return await your_model_service.get_your_models(db=db, query_params=query_params)

@router.get("/{your_model_id}", response_model=YourModelResponse)
async def get_your_model(your_model_id: int, db: AsyncSession = Depends(get_db)):
    return await your_model_service.get_your_model(db=db, your_model_id=your_model_id)

@router.put("/{your_model_id}", response_model=YourModelResponse)
async def update_your_model(*, your_model_id: int, obj_in: YourModelUpdate, db: AsyncSession = Depends(get_db)):
    return await your_model_service.update_your_model(db=db, your_model_id=your_model_id, obj_in=obj_in)

@router.delete("/{your_model_id}", response_model=YourModelResponse)
async def delete_your_model(your_model_id: int, soft_delete: bool = Query(True), db: AsyncSession = Depends(get_db)):
    return await your_model_service.delete_your_model(db=db, your_model_id=your_model_id, soft_delete=soft_delete)
```

## 6. Update `src/main.py`

```python
from src.router import tenant, your_model

app.include_router(your_model.router)
```

## 7. Update `src/models/__init__.py`

```python
from src.models.your_model import YourModel
__all__ = [..., "YourModel"]
```

## 8. Create Migration

```bash
alembic revision --autogenerate -m "Add your_model table"
alembic upgrade head
```

