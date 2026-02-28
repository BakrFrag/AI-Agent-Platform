from typing import Sequence, Optional
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.common import AbstractRepository, UUID7Str
from .models import Message
from .schemas import MessageRequest
from src.core import logger
from src.session import Session


class MessageRepository(AbstractRepository[Message, int]):
    """
    Concrete repository for Message entities. 
    Handles all direct, low-level SQLAlchemy interactions for the Message model.
    """

    def __init__(self, session: AsyncSession):
        """Initializes the repository with the active database session."""
        super().__init__(session, Message)

    async def create(self, entity: MessageRequest) -> Message:
        """
        Inserts a new message entity into the database.
        
        Args:
            entity: The message ORM object to be persisted.
        
        Returns:
            The newly created message object with generated IDs/timestamps.
        """
        
        self.session.add(entity)
        await self.session.flush() 
        await self.session.refresh(entity)
        await self.session.commit()
        logger.info(f"message created successfully with ID: {entity.id}")
        return entity
       
    
    
    async def get_message_conversion_history(self, session_id: UUID7Str, number_of_messages: int = 1) -> list[dict]:
        """
        retrieve all messages in the database and return as list of dict with role and content keys
        """
        stmt = select(Message.role, Message.content).where(Message.session_id == session_id).order_by(Message.created_at.desc())
        result = await self.session.execute(stmt)
        rows = result.all()[:number_of_messages]
        return [ {"role": r.role.value, "content": r.content} for r in rows ]
    

    async def get_session_by_id(self, entity_id: UUID7Str) -> Optional[Session]:
        """Retrieves a Session by its primary key (ID)."""
        stmt = select(Session).where(Session.id == entity_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_id(self, entity_id):
        pass 

    async def delete_by_id(self, entity_id):
        pass 

    async def update(self, message_id, messsage_data):
        pass

    async def get_all(self, session_id: UUID7Str,  skip: int = 0, limit: int = 100) -> Sequence[Message]:
        """Retrieves a list of messages with pagination. for specfic session"""
        stmt = select(Message).offset(skip).limit(limit).order_by(Message.id).where(Message.session_id == session_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

