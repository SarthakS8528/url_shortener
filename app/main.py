
from fastapi import FastAPI

from app.database import engine, Base
from app.routes import urls

# Import models so SQLAlchemy registers their metadata
from app import models


app = FastAPI(
    title="URL Shortener API",
    description="Backend service for creating and managing shortened URLs",
    version="1.0.0"
)

# Temporary table creation for our initial MVP.
# We'll replace this with Alembic migrations later.
# Base.metadata.create_all(bind=engine)


app.include_router(urls.router)


@app.get("/")
def home():
    return {
        "message": "URL Shortener API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
