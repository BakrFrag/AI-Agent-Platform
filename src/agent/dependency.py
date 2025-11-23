from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.core import get_db_async_session
from .service import AgentService

# Dependency function for service injection
def get_agent_service(session: AsyncSession = Depends(get_db_async_session)) -> AgentService:
    """Creates a Service instance tied to the request's database session."""
    return AgentService(session)