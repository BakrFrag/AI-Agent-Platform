
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.core import get_db_async_session
from .service import SessionService

# Dependency function for service injection
async def get_session_service(session: AsyncSession = Depends(get_db_async_session)) -> SessionService:
    """Creates a Service instance tied to the request's database session."""
    return SessionService(session)