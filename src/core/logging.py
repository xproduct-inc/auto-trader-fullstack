import sys
from loguru import logger
from core.config import get_settings

settings = get_settings()

def setup_logging():
    """Configure logging for the application"""
    
    # Remove default logger
    logger.remove()
    
    # Add console logger
    logger.add(
        sys.stdout,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        level="INFO"
    )
    
    # Add file logger
    logger.add(
        "logs/app.log",
        rotation="500 MB",
        retention="10 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        level="DEBUG"
    )
    
    # Add error logger
    logger.add(
        "logs/error.log",
        rotation="100 MB",
        retention="30 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        level="ERROR"
    ) 