import asyncio
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.core.config import get_settings

settings = get_settings()

async def init_db():
    """Initialize database with required data"""
    try:
        logger.info("Initializing database...")
        
        async for db in get_db():
            # Add initialization logic here
            # For example, creating default risk profiles, etc.
            pass
            
        logger.info("Database initialization completed")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(init_db()) 