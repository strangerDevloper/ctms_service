import os
from sqlalchemy import create_engine
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

# Construct database URL
# Default to PostgreSQL, but can be changed via DB_TYPE env variable
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections before using
    echo=False,  # Set to True for SQL query logging
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency function that yields a database session.
    This function handles session creation, transaction management, and cleanup.
    
    Usage in FastAPI routes:
        @app.get("/items")
        async def read_items(db: Session = Depends(get_db)):
            # Use db session here
            pass
    
    Can also be used directly outside FastAPI:
        for db in get_db():
            # Use db session here
            break
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

