"""
MongoDB database connection and management using Beanie ODM.
"""
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from app.core.config import settings
from app.models.product import Product, RawReview, AnalysisResult, ProcessingLog, Comparison


class Database:
    """Database connection manager."""
    
    client: Optional[AsyncIOMotorClient] = None
    database = None


db = Database()


async def connect_to_mongo():
    """Connect to MongoDB and initialize Beanie on application startup."""
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db.database = db.client[settings.MONGODB_DB]
    
    # Initialize Beanie with document models
    await init_beanie(
        database=db.database,
        document_models=[
            Product,
            RawReview,
            AnalysisResult,
            ProcessingLog,
            Comparison
        ]
    )
    
    print(f"Connected to MongoDB: {settings.MONGODB_DB}")
    print("Beanie initialized with document models")


async def close_mongo_connection():
    """Close MongoDB connection on application shutdown."""
    if db.client:
        db.client.close()
        print("Disconnected from MongoDB")


def get_database():
    """Get database instance."""
    return db.database


