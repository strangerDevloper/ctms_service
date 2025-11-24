# CTMS API

A modern FastAPI backend application with SQLAlchemy ORM and Alembic database migrations.

## 🚀 Features

- **FastAPI** - High-performance, modern web framework for building APIs
- **SQLAlchemy** - Powerful ORM for database operations
- **Alembic** - Database migration tool for version control
- **PostgreSQL** - Robust relational database support
- **Environment-based Configuration** - Secure configuration management via `.env` file
- **Auto-generated API Documentation** - Interactive Swagger UI and ReDoc

## 🛠️ Tech Stack

- **Python** 3.8+
- **FastAPI** 0.104.1
- **SQLAlchemy** 2.0.23
- **Alembic** 1.12.1
- **PostgreSQL** (via psycopg2-binary)
- **Uvicorn** - ASGI server

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- PostgreSQL database (or modify for your preferred database)

## ⚡ Quick Start

### 1. Clone the repository

```bash
git clone <repository-url>
cd ctms
```

### 2. Create and activate virtual environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
# Copy the example environment file
cp env.example .env

# Edit .env file with your database credentials
# DB_HOST=localhost
# DB_USER=your_db_user
# DB_PASS=your_db_password
# DB_NAME=your_database_name
# DB_PORT=5432
```

### 5. Run database migrations

```bash
# Create initial migration (if you have models)
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 6. Start the development server

```bash
uvicorn src.main:app --reload
```

### 7. Access the API

- **API Base URL**: http://localhost:8000
- **Interactive API Docs (Swagger)**: http://localhost:8000/docs
- **Alternative API Docs (ReDoc)**: http://localhost:8000/redoc

## 📁 Project Structure

```
ctms/
├── alembic/                 # Database migrations
│   ├── versions/           # Migration files
│   ├── env.py              # Alembic environment config
│   └── script.py.mako      # Migration template
├── src/
│   ├── main.py             # FastAPI application entry point
│   ├── database/           # Database configuration
│   │   ├── __init__.py
│   │   └── database.py     # Database engine, Base, and get_db()
│   ├── models/             # SQLAlchemy models
│   ├── router/             # FastAPI route handlers
│   ├── schema/             # Pydantic schemas
│   └── service/            # Business logic layer
├── alembic.ini             # Alembic configuration
├── requirements.txt        # Python dependencies
├── env.example             # Example environment variables
├── .env                    # Environment variables (create from env.example)
├── SETUP.md                # Detailed setup guide
└── README.md               # This file
```

## 🔧 Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
DB_HOST=localhost
DB_USER=your_db_user
DB_PASS=your_db_password
DB_NAME=your_database_name
DB_PORT=5432
```

**Required Variables:**

- `DB_HOST` - Database host address
- `DB_USER` - Database username
- `DB_PASS` - Database password
- `DB_NAME` - Database name
- `DB_PORT` - Database port (default: 5432)

## 📝 Database Migrations

### Create a new migration

```bash
# After creating or modifying models
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Apply to a specific revision
alembic upgrade <revision_id>
```

### Rollback migrations

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to a specific revision
alembic downgrade <revision_id>
```

### Check migration status

```bash
# Show current database revision
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic heads
```

## 💻 Development

### Creating Models

1. Create a new model file in `src/models/` (e.g., `user.py`)
2. Import `Base` from `src.database.database`
3. Define your model class

```python
from sqlalchemy import Column, Integer, String
from src.database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
```

4. Import the model in `src/models/__init__.py`

```python
from src.models.user import User

__all__ = ["User"]
```

5. Create and apply migration

```bash
alembic revision --autogenerate -m "Add User model"
alembic upgrade head
```

### Using Database Sessions in Routes

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from src.database.database import get_db

@app.get("/users")
async def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users
```

## 📚 API Endpoints

### Health Check

- **GET** `/health` - Check API health status

### Root

- **GET** `/` - Welcome message

## 🧪 Testing

(Add your testing instructions here)

## 📖 Documentation

- **Detailed Setup Guide**: See [SETUP.md](SETUP.md) for comprehensive setup instructions
- **API Documentation**: Available at http://localhost:8000/docs when server is running

## 🤝 Contributing

(Add your contributing guidelines here)

## 📄 License

(Add your license information here)

## 🐛 Troubleshooting

### Database Connection Issues

- Ensure PostgreSQL is running
- Verify `.env` file has correct credentials
- Check database exists: `psql -U your_user -d your_database`

### Migration Issues

- Ensure models are imported in `src/models/__init__.py`
- Check `alembic/env.py` is configured correctly
- Verify database URL in `.env` file

### Import Errors

- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` to install dependencies
- Check Python path includes project root

## 📞 Support

(Add your support contact information here)

---

**Happy Coding! 🎉**
