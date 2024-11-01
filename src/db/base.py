from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool

# Create a custom base class with a different name for metadata
class CustomBase:
    __abstract__ = True
    # Add any common model methods here

# Create the declarative base using our custom base class
Base = declarative_base(cls=CustomBase)

# These will be initialized in session.py
engine = None
AsyncSessionLocal = None