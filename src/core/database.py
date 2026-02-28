
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.ext.asyncio import AsyncAttrs
from src.core import settings, logger


DATABASE_URL = settings.DATABASE_URL


# This is usually only needed for SQLite, but good practice for async usage.
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

# Create the asynchronous engine
async_engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True to see SQL queries in console
    connect_args=connect_args,
    pool_recycle=3600 # Recycle connections every hour
)

# Create a session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)

# --- Dependency Injection Utility ---
async def get_db_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI Dependency that provides an asynchronous database session.

    A session is created when a request starts and is automatically closed
    when the request finishes, even if exceptions occur.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()
            
