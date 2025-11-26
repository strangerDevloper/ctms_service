# Model Creation Guide - Complete Architecture Context

This guide documents the complete architecture and patterns established for creating new models in the CTMS API.

## 📐 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Router Layer                      │
│  (API Endpoints - Request/Response Handling)                │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer                            │
│  (Business Logic - Validation - Error Handling)             │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    CRUD Layer                                │
│  (Data Access - Database Operations)                        │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Database Layer                           │
│  (SQLAlchemy Models - AsyncSession)                         │
└─────────────────────────────────────────────────────────────┘
```

## 🗂️ Project Structure

```
ctms/
├── src/
│   ├── main.py                    # FastAPI app entry point
│   ├── database/
│   │   ├── __init__.py
│   │   └── database.py            # Database config & async session
│   ├── models/
│   │   ├── __init__.py            # Import all models here
│   │   └── [model_name].py        # SQLAlchemy models
│   ├── schema/
│   │   ├── __init__.py
│   │   └── [model_name].py        # Pydantic schemas
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── base.py                # Base CRUD class (reusable)
│   │   └── [model_name].py        # Model-specific CRUD operations
│   ├── service/
│   │   ├── __init__.py
│   │   └── [model_name].py        # Business logic layer
│   └── router/
│       ├── __init__.py
│       └── [model_name].py        # API route handlers
├── alembic/                       # Database migrations
├── requirements.txt
└── .env                           # Environment variables
```

## 🎯 Complete Pattern Breakdown

### 1. **Model Layer** (`src/models/`)

**Purpose**: Define SQLAlchemy database models

**Example Structure**:

```python
from sqlalchemy import Column, Integer, String
from src.database import Base

class YourModel(Base):
    __tablename__ = "your_table"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    # ... other columns
```

**Key Points**:

- Inherit from `Base` (from `src.database`)
- Use `__tablename__` to specify table name
- Set `schema="public"` if using PostgreSQL schemas
- Import in `models/__init__.py` for Alembic detection

### 2. **Schema Layer** (`src/schema/`)

**Purpose**: Pydantic schemas for request/response validation

**Required Schemas**:

```python
from pydantic import BaseModel, Field
from typing import Optional
from src.models.your_model import YourModelStatus  # if you have enums

# Base schema with common fields
class YourModelBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    # ... common fields

# Create schema
class YourModelCreate(YourModelBase):
    pass  # Add creation-specific fields if needed

# Update schema (all fields optional)
class YourModelUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    # ... other optional

# Full response schema
class YourModelResponse(YourModelBase):
    id: int
    created_at: datetime
    updated_at: datetime
    # ... all fields

    class Config:
        from_attributes = True

# List response schema (simplified)
class YourModelListResponse(BaseModel):
    id: int
    name: str
    # ... only essential fields

    class Config:
        from_attributes = True

# Query parameters schema
class YourModelQueryParams(BaseModel):
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=1000)
    status: Optional[YourModelStatus] = Field(default=None)
    search: Optional[str] = Field(default=None)
    # ... other filters

    class Config:
        from_attributes = True
```

### 3. **CRUD Layer** (`src/crud/`)

**Purpose**: Database operations (Create, Read, Update, Delete)

**Base CRUD** (`crud/base.py`):

- Provides common operations: `get`, `get_multi`, `create`, `update`, `delete`, `soft_delete`
- Uses async SQLAlchemy patterns
- Generic and reusable for all models

**Model-Specific CRUD** (`crud/[model_name].py`):

```python
from typing import List, Optional
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from src.crud.base import CRUDBase
from src.models.your_model import YourModel
from src.schema.your_model import YourModelCreate, YourUpdate, YourQueryParams

class CRUDYourModel(CRUDBase[YourModel, YourCreate, YourUpdate]):
    """
    CRUD operations for YourModel.
    Extends base CRUD with model-specific operations.
    """

    async def get_by_field(self, db: AsyncSession, *, field_name: str, field_value: Any) -> Optional[YourModel]:
        """Get by a specific field."""
        result = await db.execute(
            select(YourModel).filter(getattr(YourModel, field_name) == field_value)
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        query_params: YourQueryParams
    ) -> List[YourModel]:
        """Get multiple records with filters."""
        query = select(YourModel)

        # Apply filters from query_params
        if query_params.status:
            query = query.filter(YourModel.status == query_params.status)

        if query_params.search:
            search_pattern = f"%{query_params.search}%"
            query = query.filter(YourModel.name.ilike(search_pattern))

        query = query.offset(query_params.skip).limit(query_params.limit)
        result = await db.execute(query)
        return list(result.scalars().all())

# Create instance
your_model = CRUDYourModel(YourModel)
```

### 4. **Service Layer** (`src/service/`)

**Purpose**: Business logic, validation, error handling

```python
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.crud.your_model import your_model as crud_your_model
from src.models.your_model import YourModel
from src.schema.your_model import YourCreate, YourUpdate, YourQueryParams

class YourModelService:
    """Service layer for YourModel operations."""

    @staticmethod
    async def get_your_model(db: AsyncSession, your_model_id: int) -> YourModel:
        """Get a record by ID."""
        obj = await crud_your_model.get(db=db, id=your_model_id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"YourModel with ID {your_model_id} not found"
            )
        return obj

    @staticmethod
    async def get_your_models(
        db: AsyncSession,
        query_params: YourQueryParams
    ) -> List[YourModel]:
        """Get multiple records with filters."""
        return await crud_your_model.get_multi(db=db, query_params=query_params)

    @staticmethod
    async def create_your_model(db: AsyncSession, obj_in: YourCreate) -> YourModel:
        """Create a new record."""
        # Business logic validation
        existing = await crud_your_model.get_by_field(
            db=db, field_name="name", field_value=obj_in.name
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"YourModel with name '{obj_in.name}' already exists"
            )

        return await crud_your_model.create(db=db, obj_in=obj_in)

    @staticmethod
    async def update_your_model(
        db: AsyncSession,
        your_model_id: int,
        obj_in: YourUpdate
    ) -> YourModel:
        """Update an existing record."""
        obj = await YourModelService.get_your_model(db=db, your_model_id=your_model_id)
        return await crud_your_model.update(db=db, db_obj=obj, obj_in=obj_in)

    @staticmethod
    async def delete_your_model(
        db: AsyncSession,
        your_model_id: int,
        soft_delete: bool = True
    ) -> YourModel:
        """Delete a record."""
        obj = await YourModelService.get_your_model(db=db, your_model_id=your_model_id)

        if soft_delete:
            return await crud_your_model.soft_delete(db=db, id=your_model_id)
        else:
            return await crud_your_model.delete(db=db, id=your_model_id)

# Create instance
your_model_service = YourModelService()
```

### 5. **Router Layer** (`src/router/`)

**Purpose**: API endpoints, request/response handling

```python
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.service.your_model import your_model_service
from src.schema.your_model import (
    YourCreate,
    YourUpdate,
    YourResponse,
    YourListResponse,
    YourQueryParams
)

router = APIRouter(
    prefix="/your-model",  # URL prefix
    tags=["Your Models"],
    responses={404: {"description": "Not found"}},
)

@router.post(
    "",
    response_model=YourResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new your model",
    description="Create a new your model"
)
async def create_your_model(
    *,
    db: AsyncSession = Depends(get_db),
    obj_in: YourCreate
):
    """Create a new your model."""
    return await your_model_service.create_your_model(db=db, obj_in=obj_in)

@router.get(
    "",
    response_model=List[YourListResponse],
    summary="Get all your models",
    description="Retrieve a list with pagination and filters"
)
async def get_your_models(
    query_params: YourQueryParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Get all your models with filters."""
    return await your_model_service.get_your_models(
        db=db,
        query_params=query_params
    )

@router.get(
    "/{your_model_id}",
    response_model=YourResponse,
    summary="Get your model by ID"
)
async def get_your_model(
    your_model_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a your model by ID."""
    return await your_model_service.get_your_model(db=db, your_model_id=your_model_id)

@router.put(
    "/{your_model_id}",
    response_model=YourResponse,
    summary="Update your model"
)
async def update_your_model(
    *,
    your_model_id: int,
    obj_in: YourUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a your model."""
    return await your_model_service.update_your_model(
        db=db,
        your_model_id=your_model_id,
        obj_in=obj_in
    )

@router.delete(
    "/{your_model_id}",
    response_model=YourResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete your model"
)
async def delete_your_model(
    your_model_id: int,
    soft_delete: bool = Query(True),
    db: AsyncSession = Depends(get_db)
):
    """Delete a your model."""
    return await your_model_service.delete_your_model(
        db=db,
        your_model_id=your_model_id,
        soft_delete=soft_delete
    )
```

### 6. **Register Router** (`src/main.py`)

```python
from fastapi import FastAPI
from src.router import tenant, your_model  # Import your router

app = FastAPI(title="CTMS API", version="1.0.0")

# Include routers
app.include_router(tenant.router)
app.include_router(your_model.router)  # Add your router
```

## 🚀 Step-by-Step: Creating a New Model

### Step 1: Create the Model

```bash
# Create file: src/models/your_model.py
```

**Template**:

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

### Step 2: Import in Models Init

```python
# src/models/__init__.py
from src.models.your_model import YourModel
__all__ = [..., "YourModel"]
```

### Step 3: Create Schemas

```bash
# Create file: src/schema/your_model.py
```

- `YourModelBase`
- `YourModelCreate`
- `YourModelUpdate`
- `YourModelResponse`
- `YourModelListResponse`
- `YourModelQueryParams`

### Step 4: Create CRUD

```bash
# Create file: src/crud/your_model.py
```

- Extend `CRUDBase`
- Add model-specific methods
- Create instance: `your_model = CRUDYourModel(YourModel)`

### Step 5: Create Service

```bash
# Create file: src/service/your_model.py
```

- Business logic
- Error handling
- Validation
- Create instance: `your_model_service = YourModelService()`

### Step 6: Create Router

```bash
# Create file: src/router/your_model.py
```

- Define all endpoints
- Use `Depends()` for query params and database
- Register in `main.py`

### Step 7: Create Migration

```bash
alembic revision --autogenerate -m "Add your_model table"
alembic upgrade head
```

## 🔑 Key Patterns & Best Practices

### 1. **Async Everywhere**

- All functions are `async def`
- Use `AsyncSession` from `sqlalchemy.ext.asyncio`
- Use `await` for all database operations
- Use `select()` instead of `query()`

### 2. **Query Parameters Pattern**

- Create `QueryParams` schema in schema file
- Use `Depends()` in router
- Pass object through Service → CRUD
- Access attributes directly: `query_params.skip`

### 3. **Error Handling**

- Use `HTTPException` in Service layer
- Return appropriate status codes
- Provide clear error messages

### 4. **Response Schemas**

- `ListResponse` for list endpoints (simplified fields)
- `Response` for single item endpoints (full object)
- Use `from_attributes = True` in Config

### 5. **Soft Delete Pattern**

- Add `is_deleted` column to models
- Filter in queries: `filter(Model.is_deleted == False)`
- Use `soft_delete()` method in CRUD

## 📝 Complete Example: Tenant Model

See the existing `Tenant` model implementation as a reference:

- `src/models/tenants.py` - Model definition
- `src/schema/tenant.py` - All schemas
- `src/crud/tenant.py` - CRUD operations
- `src/service/tenant.py` - Business logic
- `src/router/tenant.py` - API endpoints

## 🎯 Quick Checklist for New Model

- [ ] Create model in `src/models/[name].py`
- [ ] Import in `src/models/__init__.py`
- [ ] Create schemas in `src/schema/[name].py`
- [ ] Create CRUD in `src/crud/[name].py`
- [ ] Create service in `src/service/[name].py`
- [ ] Create router in `src/router/[name].py`
- [ ] Register router in `src/main.py`
- [ ] Create Alembic migration
- [ ] Test endpoints

## 🔧 Database Configuration

**Async Session Setup** (`src/database/database.py`):

- Uses `create_async_engine` with `asyncpg`
- `AsyncSessionLocal` for async operations
- `get_db()` dependency function yields async session

**Usage**:

```python
async def endpoint(db: AsyncSession = Depends(get_db)):
    # Use db here
    pass
```

## 📚 Additional Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy Async**: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- **Pydantic**: https://docs.pydantic.dev/

---

**This architecture ensures consistency, maintainability, and scalability across all models in your application.**
