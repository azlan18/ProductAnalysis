"""
Main FastAPI application.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import connect_to_mongo, close_mongo_connection
from app.core.logging_config import setup_logging
from app.api.v1 import products, compare, status


# Setup logging first
setup_logging()


app = FastAPI(
    title="Product Analysis API",
    description="API for product sentiment analysis and comparison",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products.router, prefix="/api/v1")
app.include_router(compare.router, prefix="/api/v1")
app.include_router(status.router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup."""
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown."""
    await close_mongo_connection()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Product Analysis API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

