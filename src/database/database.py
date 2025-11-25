import os
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database configuration from environment variables
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT", "5432")  # Default PostgreSQL port

# Validate required environment variables
if not all([DB_HOST, DB_USER, DB_PASS, DB_NAME]):
    raise ValueError(
        "Missing required database environment variables: "
        "DB_HOST, DB_USER, DB_PASS, DB_NAME must be set"
    )

# Construct database URL (sync for Alembic)
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Construct async database URL
ASYNC_DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create SQLAlchemy engine (sync - for Alembic)
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    echo=False,
)

# Create async SQLAlchemy engine
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    echo=False,
)

# Create SessionLocal class (sync - for Alembic)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create AsyncSessionLocal class
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Create Base class for models
Base = declarative_base()


async def get_db():
    """
    Async dependency function that yields a database session.
    This function handles session creation, transaction management, and cleanup.
    
    Usage in FastAPI routes:
        @app.get("/items")
        async def read_items(db: AsyncSession = Depends(get_db)):
            # Use db session here
            pass
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

