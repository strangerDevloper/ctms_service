# CTMS API - Complete Architecture Context

This document provides a comprehensive overview of the CTMS API architecture, patterns, and implementation details.

## 📐 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Router Layer                      │
│  (API Endpoints - Request/Response Handling)                │
│  + Profiling Middleware (Request/Response Logging)          │
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
│   │   ├── tenants.py             # Tenant model
│   │   ├── sports.py              # Sport model
│   │   ├── tenant_sports_mapping.py # Tenant-Sport mapping model
│   │   └── [other_models].py
│   ├── schema/
│   │   ├── __init__.py
│   │   ├── tenant.py              # Tenant Pydantic schemas
│   │   ├── sports.py              # Sport Pydantic schemas
│   │   ├── tenant_sports_mapping.py # Mapping schemas
│   │   └── [other_schemas].py
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── base.py                # Base CRUD class (reusable)
│   │   ├── tenant.py              # Tenant CRUD operations
│   │   ├── sports.py              # Sport CRUD operations
│   │   ├── tenant_sports_mapping.py # Mapping CRUD operations
│   │   └── [other_crud].py
│   ├── service/
│   │   ├── __init__.py
│   │   ├── tenant.py              # Tenant business logic
│   │   ├── sports.py              # Sport business logic
│   │   ├── tenant_sports_mapping.py # Mapping business logic
│   │   └── [other_services].py
│   ├── router/
│   │   ├── __init__.py
│   │   ├── tenant.py              # Tenant API routes
│   │   ├── sports.py              # Sport API routes
│   │   └── [other_routers].py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── response.py            # Standard response formatter
│   └── middleware/
│       ├── __init__.py
│       └── profiling.py          # Request/Response profiling middleware
├── alembic/                       # Database migrations
├── requirements.txt
├── .env                           # Environment variables
└── env.example                    # Environment variables template
```

## 🎯 Core Patterns & Components

### 1. Standard Response Format

All API responses follow a consistent format:

```json
{
    "data": <response_data>,
    "msg": "Success message",
    "status": <http_status_code>
}
```

**Implementation**: `src/utils/response.py`
- `FormatResponse` class with static methods:
  - `success()` - For successful operations (200)
  - `created()` - For resource creation (201)
  - `error()` - For error responses
  - `not_found()` - For 404 errors
  - `bad_request()` - For 400 errors

**Usage**:
```python
from src.utils.response import FormatResponse

return FormatResponse.success(
    data=result,
    msg="Operation completed successfully"
)
```

### 2. Pagination Pattern

List endpoints return paginated data with metadata:

```json
{
    "data": {
        "items": [...],
        "total_count": 100,
        "has_next_page": true,
        "skip": 0,
        "limit": 100
    },
    "msg": "Retrieved 100 items out of 100 total",
    "status": 200
}
```

**Implementation**: `src/utils/response.py`
- `PaginatedData` model with items, total_count, has_next_page, skip, limit

### 3. CRUD Layer Pattern

**Base CRUD** (`src/crud/base.py`):
- Generic CRUD operations: `get`, `get_multi`, `create`, `update`, `delete`, `soft_delete`
- Uses async SQLAlchemy patterns
- Reusable for all models

**Model-Specific CRUD**:
- Extends `CRUDBase`
- Adds model-specific methods (e.g., `get_by_code`, `get_by_status`)
- Uses optimized queries with filters

**Key Pattern - Filter Application**:
```python
def _apply_filters(self, query, query_params):
    """Centralized filter logic reused for count and data queries."""
    # Apply all filters
    return query
```

### 4. Service Layer Pattern

**Responsibilities**:
- Business logic validation
- Error handling with HTTPException
- Data transformation (SQLAlchemy → Pydantic)
- Orchestrates CRUD operations

**Validation Pattern**:
- Validates entity existence before operations
- Uses count-based validation for bulk operations
- Provides clear error messages

### 5. Router Layer Pattern

**Standard Endpoints**:
- `POST /resource` - Create
- `GET /resource` - List with pagination
- `GET /resource/{id}` - Get by ID
- `PUT /resource/{id}` - Update
- `DELETE /resource/{id}` - Delete (soft/hard)

**Response Models**:
- Uses `StandardResponse[DataType]` for type safety
- Paginated endpoints use `StandardResponse[PaginatedData[ListResponse]]`

## 📦 Implemented Modules

### 1. Tenant Module

**Model**: `src/models/tenants.py`
- Fields: id, name, tenant_code, tenant_uuid, logo, address, email, description, status, timestamps, is_deleted
- Relationships: sports_mappings

**Schemas**: `src/schema/tenant.py`
- `TenantBase`, `TenantCreate`, `TenantUpdate`
- `TenantResponse`, `TenantListResponse`
- `TenantQueryParams` (with sports_id filter)

**CRUD**: `src/crud/tenant.py`
- `get_by_code()`, `get_by_uuid()`, `get_active_tenants()`
- `get_multi()` with optimized filter application
- Supports filtering by sports_id (joins with tenant_sports_mapping)

**Service**: `src/service/tenant.py`
- `get_tenant()` with optional `include_sports` flag
- `get_tenants()` returns paginated data
- All CRUD operations with validation

**Router**: `src/router/tenant.py`
- Standard CRUD endpoints
- `GET /tenant/{id}?include_sports=true` - Optional sports mappings
- `GET /tenant?sports_id={id}` - Filter by sport

### 2. Sports Module

**Model**: `src/models/sports.py`
- Fields: id, sport_code, sport_name, category, icon_url, status, description, timestamps, is_deleted
- Enums: SportCategory, SportStatus

**Schemas**: `src/schema/sports.py`
- `SportBase`, `SportCreate`, `SportUpdate`
- `SportResponse`, `SportListResponse`
- `SportQueryParams` (with category filter)

**CRUD**: `src/crud/sports.py`
- `get_by_code()`, `get_active_sports()`, `get_by_status()`, `get_by_category()`
- `validate_sports_exist()` - Bulk validation with IN query
- `get_multi()` with pagination

**Service**: `src/service/sports.py`
- All CRUD operations
- Returns paginated data for list endpoints

**Router**: `src/router/sports.py`
- Standard CRUD endpoints
- All responses use standard format

### 3. Tenant-Sports Mapping Module

**Model**: `src/models/tenant_sports_mapping.py`
- Fields: id, tenant_id, sport_id, status, created_by, updated_by, desciption, timestamps
- Enums: MappingStatus
- Relationships: tenant, sport

**Schemas**: `src/schema/tenant_sports_mapping.py`
- `TenantSportsMappingBase`, `TenantSportsMappingCreate`, `TenantSportsMappingUpdate`
- `TenantSportsMappingResponse`
- `RegisterSportItem`, `BulkRegisterSportRequest`

**CRUD**: `src/crud/tenant_sports_mapping.py`
- `get_by_tenant_and_sport()`, `get_by_tenant()`, `get_by_sport()`
- `count_existing_mappings()` - Count-based duplicate check
- `bulk_create()` - Bulk insert operation

**Service**: `src/service/tenant_sports_mapping.py`
- `register_sport()` - Single sport registration
- `bulk_register_sports()` - Multiple sports registration
- `update_mapping_by_tenant_sport()` - Update/unregister sport
- Optimized validation using count-based queries

**Router**: `src/router/tenant.py` (under tenant routes)
- `POST /tenant/{tenant_id}/sports` - Register sports (bulk)
- `PUT /tenant/{tenant_id}/sports/{sport_id}` - Update/unregister sport

## 🔧 Key Features

### 1. Optimized Query Patterns

**Single Query with IN Clause**:
```python
# Instead of N queries, use single IN query
query = select(Sport.id, Sport.is_deleted).filter(Sport.id.in_(sport_ids))
```

**Count-Based Validation**:
```python
# Instead of checking each mapping, count all at once
count = await crud_mapping.count_existing_mappings(
    db=db, tenant_id=tenant_id, sport_ids=sport_ids
)
if count > 0:
    raise HTTPException(...)
```

**Filter Reusability**:
```python
# Apply filters once, reuse for count and data queries
base_query = self._apply_filters(select(Model), query_params)
count_query = self._apply_filters(select(func.count()), query_params)
```

### 2. Bulk Operations

**Bulk Create**:
```python
# Single transaction for multiple inserts
db_objs = [Model(**data) for data in mappings]
db.add_all(db_objs)
await db.commit()
```

**Bulk Validation**:
- Validates multiple entities in single query
- Count comparison for validation
- Generic error messages

### 3. Profiling Middleware

**Location**: `src/middleware/profiling.py`

**Features**:
- Logs all API requests with response time
- Similar to Morgan middleware in Node.js
- Configurable log formats
- Can be disabled via environment variable

**Log Formats**:
- `combined` (default): Full details with IP, method, path, status, size, referrer, user-agent, time
- `dev`: Short format - `METHOD PATH STATUS TIME`
- `short`: With IP - `IP METHOD PATH STATUS TIME`
- `tiny`: Minimal - `METHOD STATUS TIME`

**Configuration** (`.env`):
```env
ENABLE_PROFILING=true
PROFILE_LOG_FORMAT=combined
```

**Example Log Output**:
```
127.0.0.1 - - [25/Dec/2024:10:30:45 +0000] "GET /tenant?skip=0&limit=100 HTTP/1.1" 200 1234 "-" "Mozilla/5.0..." 45.23ms
```

### 4. Response Headers

Middleware adds custom headers:
- `X-Process-Time`: Response time in milliseconds
- `X-Response-Time`: Response time in milliseconds

## 🚀 API Endpoints

### Tenant Endpoints

- `POST /tenant` - Create tenant
- `GET /tenant` - List tenants (with pagination, filters, sports_id filter)
- `GET /tenant/{tenant_id}` - Get tenant by ID (optional `include_sports` flag)
- `GET /tenant/code/{tenant_code}` - Get tenant by code
- `PUT /tenant/{tenant_id}` - Update tenant
- `DELETE /tenant/{tenant_id}` - Delete tenant (soft/hard)
- `POST /tenant/{tenant_id}/sports` - Register sports (bulk)
- `PUT /tenant/{tenant_id}/sports/{sport_id}` - Update/unregister sport mapping

### Sports Endpoints

- `POST /sport` - Create sport
- `GET /sport` - List sports (with pagination, filters)
- `GET /sport/{sport_id}` - Get sport by ID
- `GET /sport/code/{sport_code}` - Get sport by code
- `PUT /sport/{sport_id}` - Update sport
- `DELETE /sport/{sport_id}` - Delete sport (soft/hard)

## 🔑 Best Practices Implemented

### 1. Async Everywhere
- All functions use `async def`
- `AsyncSession` from `sqlalchemy.ext.asyncio`
- `await` for all database operations
- `select()` instead of deprecated `query()`

### 2. Error Handling
- `HTTPException` in Service layer
- Appropriate status codes
- Clear, descriptive error messages
- Generic messages for bulk operations

### 3. Validation
- Entity existence validation before operations
- Duplicate prevention
- Count-based validation for performance
- Early exit patterns

### 4. Query Optimization
- Single queries with IN clauses instead of loops
- Count-based checks instead of individual lookups
- Filter reusability (DRY principle)
- Bulk operations for inserts

### 5. Code Organization
- Separation of concerns (Router → Service → CRUD → Database)
- Reusable base classes
- Centralized filter logic
- Consistent naming conventions

## 📝 Environment Configuration

### Database
```env
DB_HOST=localhost
DB_USER=your_db_user
DB_PASS=your_db_password
DB_NAME=your_database_name
DB_PORT=5432
```

### Profiling Middleware
```env
ENABLE_PROFILING=true          # Enable/disable profiling (default: false)
PROFILE_LOG_FORMAT=combined    # Log format: combined, dev, short, tiny
```

## 🎯 Response Format Examples

### Success Response
```json
{
    "data": {
        "id": 1,
        "name": "Example",
        ...
    },
    "msg": "Operation completed successfully",
    "status": 200
}
```

### Paginated Response
```json
{
    "data": {
        "items": [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"}
        ],
        "total_count": 100,
        "has_next_page": true,
        "skip": 0,
        "limit": 100
    },
    "msg": "Retrieved 100 items out of 100 total",
    "status": 200
}
```

### Error Response
```json
{
    "data": null,
    "msg": "Resource not found",
    "status": 404
}
```

## 🔄 Data Flow Example

**Request**: `POST /tenant/1/sports`

1. **Router** (`src/router/tenant.py`)
   - Receives request
   - Validates request body
   - Calls service

2. **Service** (`src/service/tenant_sports_mapping.py`)
   - Validates tenant exists (count query)
   - Validates sports exist (single IN query)
   - Checks for duplicates (count query)
   - Prepares bulk create data
   - Calls CRUD bulk_create

3. **CRUD** (`src/crud/tenant_sports_mapping.py`)
   - Executes bulk insert
   - Returns created objects

4. **Service** → **Router**
   - Formats response using FormatResponse
   - Returns standard response format

5. **Middleware** (`src/middleware/profiling.py`)
   - Logs request/response
   - Adds response time headers

## 📊 Performance Optimizations

1. **Bulk Operations**: Single transaction for multiple inserts
2. **IN Queries**: Single query instead of N queries
3. **Count-Based Validation**: Count queries instead of fetching all records
4. **Filter Reusability**: Apply filters once, reuse for count and data
5. **Early Exit**: Check duplicates before expensive validations

## 🛠️ Development Guidelines

### Creating New Models

Follow the established pattern:
1. Create model in `src/models/`
2. Import in `src/models/__init__.py`
3. Create schemas in `src/schema/`
4. Create CRUD in `src/crud/` (extend CRUDBase)
5. Create service in `src/service/`
6. Create router in `src/router/`
7. Register router in `src/main.py`
8. Create Alembic migration

### Response Formatting

Always use `FormatResponse`:
```python
return FormatResponse.success(data=result, msg="Success message")
return FormatResponse.created(data=result, msg="Created successfully")
```

### Error Handling

Use HTTPException in Service layer:
```python
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Clear error message"
)
```

### Query Optimization

- Use IN clauses for multiple IDs
- Use count queries for existence checks
- Reuse filter logic for count and data queries
- Use bulk operations for multiple inserts

---

**This architecture ensures consistency, maintainability, scalability, and performance across all modules in the CTMS API.**

