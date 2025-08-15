"""
MongoDB Database Configuration using Beanie ODM.
"""

import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from ..models.quiz import Quiz, Question, Answer, QuizSession
from .settings import get_settings

logger = logging.getLogger(__name__)

# Global MongoDB client instance
mongodb_client: Optional[AsyncIOMotorClient] = None


async def init_beanie():
    """Initialize Beanie ODM with MongoDB connection."""
    global mongodb_client
    
    settings = get_settings()
    
    try:
        # Create MongoDB client
        mongodb_client = AsyncIOMotorClient(settings.mongodb_url)
        
        # Get database
        database = mongodb_client[settings.mongodb_database]
        
        # Initialize Beanie with document models
        await init_beanie(
            database=database,
            document_models=[Quiz, Question, Answer, QuizSession],
        )
        
        logger.info("MongoDB connection and Beanie ODM initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize MongoDB connection: {e}")
        raise


async def close_beanie():
    """Close MongoDB connection."""
    global mongodb_client
    
    if mongodb_client:
        mongodb_client.close()
        mongodb_client = None
        logger.info("MongoDB connection closed")


def get_mongodb_client() -> Optional[AsyncIOMotorClient]:
    """Get the MongoDB client instance."""
    return mongodb_client
