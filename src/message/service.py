from typing import Sequence
from .repository import MessageRepository
from .models import Message
from .schemas import MessageResponse, TextMessageRequest, MessageRole, MessageType
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from src.core import logger

class MessageService:
    """
    Service layer for Message business logic, orchestrating Repository calls.
    """
    def __init__(self, session: AsyncSession):
        self.repository = MessageRepository(session)
    
    
    async def add_message(self, message_data: TextMessageRequest) -> Message:
        """Creates a new message with basic validation."""
        new_message = Message(**message_data.model_dump())
        return await self.repository.create(new_message)

    async def list_session_messages(self,session_id: int, skip: int = 0, limit: int = 100) -> Sequence[Message]:
        """Lists all messages by session id with pagination."""
        return await self.repository.get_all(session_id = session_id, skip=skip, limit=limit)