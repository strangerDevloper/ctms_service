# FastAPI + SQLAlchemy + Alembic Setup Guide

## Prerequisites

- Python 3.8+ installed
- pip installed

## Setup Sequence

### 1. Create and activate virtual environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create .env file

```bash
# Copy the example env file
cp env.example .env

# Or create .env manually with the following variables:
# DB_HOST=localhost
# DB_USER=your_db_user
# DB_PASS=your_db_password
# DB_NAME=your_database_name
# DB_PORT=5432
```

**Required Environment Variables:**

- `DB_HOST` - Database host (e.g., localhost)
- `DB_USER` - Database username
- `DB_PASS` - Database password
- `DB_NAME` - Database name
- `DB_PORT` - Database port (default: 5432 for PostgreSQL)

### 4. Initialize Alembic (if not already initialized)

```bash
# Initialize Alembic (this creates the alembic directory structure)
alembic init alembic
```

**Note:** The alembic directory and configuration files are already created, so you can skip this step.

### 5. Create your first model

Create a model file in `src/models/` (e.g., `src/models/user.py`):

```python
from sqlalchemy import Column, Integer, String
from src.database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
```

**Important:** Always import `Base` from `src.database.database`, not create a new one.

### 6. Import models in src/models/**init**.py

After creating your models, import them in `src/models/__init__.py` so Alembic can detect them:

```python
from src.models.user import User

__all__ = ["User"]
```

**Note:** The `alembic/env.py` file is already configured to automatically import all models from `src.models`, so you don't need to modify it manually.

### 7. Create initial migration

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# This will create a migration file in alembic/versions/
```

### 8. Apply migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Or apply to a specific revision
# alembic upgrade <revision_id>
```

### 9. Run the FastAPI server

```bash
# Run with uvicorn
uvicorn src.main:app --reload

# Or specify host and port
# uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 10. Access the API

- API: http://localhost:8000
- Interactive API docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## Common Alembic Commands

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Rollback to a specific revision
alembic downgrade <revision_id>

# Show current revision
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic heads
```

## Project Structure

```
ctms/
├── alembic/
│   ├── versions/          # Migration files
│   ├── env.py            # Alembic environment config (reads from .env)
│   └── script.py.mako    # Migration template
├── src/
│   ├── main.py           # FastAPI app entry point
│   ├── database/         # Database configuration folder
│   │   ├── __init__.py
│   │   └── database.py   # Database engine, session setup, and get_db() function
│   ├── models/           # SQLAlchemy models
│   ├── router/           # FastAPI routers
│   ├── schema/           # Pydantic schemas
│   └── service/          # Business logic
├── alembic.ini           # Alembic configuration
├── requirements.txt      # Python dependencies
├── env.example           # Example environment variables file
└── .env                  # Environment variables (create from env.example)
```

## Database Configuration

The database configuration is centralized in `src/database/database.py`:

- **Reads from `.env` file**: Uses `DB_HOST`, `DB_USER`, `DB_PASS`, `DB_NAME`, `DB_PORT` environment variables
- **Creates SQLAlchemy engine**: With connection pooling (pool_size=20, max_overflow=10)
- **Provides `Base`**: Declarative base for all models
- **Provides `get_db()`**: Dependency function for FastAPI routes that yields database sessions
- **Automatic transaction management**: Commits on success, rolls back on error, always closes session

**Current Setup:** PostgreSQL (can be modified in `database.py` if needed)

**Alembic Integration:** The `alembic/env.py` file is configured to:

- Automatically read database credentials from `.env` file
- Import `Base` from `src.database.database`
- Import all models from `src.models`
- Generate migrations based on your models

### Using Database Sessions in Routes

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from src.database.database import get_db

@app.get("/items")
async def read_items(db: Session = Depends(get_db)):
    # Use db session here
    items = db.query(Item).all()
    return items
```

## Quick Start Checklist

1. ✅ Create and activate virtual environment
2. ✅ Install dependencies: `pip install -r requirements.txt`
3. ✅ Create `.env` file with database credentials (copy from `env.example`)
4. ✅ Create your models in `src/models/` (import `Base` from `src.database.database`)
5. ✅ Import models in `src/models/__init__.py`
6. ✅ Create migration: `alembic revision --autogenerate -m "Initial migration"`
7. ✅ Apply migration: `alembic upgrade head`
8. ✅ Run server: `uvicorn src.main:app --reload`

## Next Steps

1. Create your models in `src/models/` (remember to import `Base` from `src.database.database`)
2. Import models in `src/models/__init__.py` so Alembic can detect them
3. Create Pydantic schemas in `src/schema/`
4. Create API routers in `src/router/`
5. Create service layer in `src/service/`
6. Import and register routers in `src/main.py`
7. Use `get_db` from `src.database.database` as a dependency in your routes
