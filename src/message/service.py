from typing import Sequence
from .repository import MessageRepository
from .models import Message as MessageModel
from .schemas import Message, MessageRequest, MessageRole, MessageType
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from src.core import logger
from src.llm_interaction.openai_client import AsyncOpenAIClient
from src.session.service import SessionService
class MessageService:
    """
    Service layer for Message business logic, orchestrating Repository calls.
    """
    def __init__(self, session: AsyncSession):
        self.repository = MessageRepository(session)
        self.client = AsyncOpenAIClient()
        self.session_service = SessionService(session)
    
    def generate_assistant_message(self, message_data: MessageRequest) -> MessageModel:
        """Creates a new assistant message."""
        message_data = MessageRequest(
            session_id= message_data.session_id,
            role=MessageRole.ASSISTANT,
            type=MessageType.TEXT,
            content= message_data.content
        )
        return MessageModel(**message_data.model_dump())

    def generate_user_message(self, message_data: MessageRequest) -> MessageModel:
        """Creates a new user message."""
        message_data = MessageRequest(
            session_id= message_data.session_id,
            role=MessageRole.USER,
            type=MessageType.TEXT,
            content= message_data.content
        )
        return MessageModel(**message_data.model_dump())
    
        
    async def add_message(self, message_data: MessageRequest) -> Message:

        """Creates a new message with basic validation."""
        print("at begging ----------------------------------------- of add_message")
        print(message_data)
        message = self.generate_user_message(message_data) if message_data.role == MessageRole.USER else self.generate_assistant_message(message_data)
        print("message ---->", message)
        return await self.repository.create(message)


    async def list_session_messages(self,session_id: int, skip: int = 0, limit: int = 100) -> Sequence[Message]:
        """Lists all messages by session id with pagination."""
        return await self.repository.get_all(session_id = session_id, skip=skip, limit=limit)
    

    async def receive_message(self, message_data: MessageRequest) -> Message:
        """Handles receiving a new message and returns the created message."""
        session_object =  await self.session_service.get_session_by_id(message_data.session_id)   
        print("session_object:", session_object)
        created_message = await self.add_message(message_data)
        print("created_message:", created_message)
        ai_content = await self.client.generate_llm_response(
            session_id = created_message.session_id, 
            content =  created_message.content
          #  prompt = session_object.agent.prompt, 
        )
        print(ai_content)
        ai_message_data = MessageRequest(
                session_id=created_message.session_id,
                role=MessageRole.ASSISTANT,
                type=MessageType.TEXT,
                content=ai_content
            )
        ai_message = await self.add_message(ai_message_data)
        return ai_message