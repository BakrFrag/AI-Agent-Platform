from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.core import get_db_async_session
from src.common import AbstractRepository
from .repository import AgentRepository
# Dependency function for service injection
async def get_agent_repository(session: AsyncSession = Depends(get_db_async_session)) -> AbstractRepository:
    """Creates a Service instance tied to the request's database session."""
    return AgentRepository(session)