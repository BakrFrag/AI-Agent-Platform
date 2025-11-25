from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.core import get_db_async_session
from .service import MessageService

# Dependency function for service injection
async def get_message_service(session: AsyncSession = Depends(get_db_async_session)) -> MessageService:
    """Creates a Service instance tied to the request's database session."""
    return MessageService(session)