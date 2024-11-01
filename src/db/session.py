from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from src.core.config import get_settings

settings = get_settings()

# Use localhost when running API locally, db when running in Docker
host = "localhost" if settings.ENVIRONMENT == "development" else "db"
DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{host}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

engine = create_async_engine(
    DATABASE_URL,
    echo=settings.ENABLE_DEBUG_MODE,
    pool_size=settings.POOL_SIZE,
    max_overflow=10
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close() 