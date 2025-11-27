import os
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from src.database import Base, engine
from src.router import tenant, sports
from src.middleware.profiling import ProfilingMiddleware

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CTMS API", version="1.0.0")

# Add profiling middleware (similar to Morgan in Node.js)
# Enable/disable via ENABLE_PROFILING env variable (default: true)
# Log format via PROFILE_LOG_FORMAT env variable (default: "combined")
enable_profiling = os.getenv("ENABLE_PROFILING", "False").lower() == "true"
if enable_profiling:
    log_format = os.getenv("PROFILE_LOG_FORMAT", "combined")
    app.add_middleware(ProfilingMiddleware, log_format=log_format)

# Include routers
app.include_router(tenant.router)
app.include_router(sports.router)


@app.get("/")
def read_root():
    """
    Endpoint to welcome the user to the API.
    """
    return {"message": "Welcome to CTMS API"}


@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """
    Endpoint to check the health of the API.
    """
    return JSONResponse(content={"status": "healthy"})

origins = ["http://localhost:4200","http://20.56.90.56:8030","http://20.56.90.56:8035"]
# origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
