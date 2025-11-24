from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from src.database import Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CTMS API", version="1.0.0")


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

