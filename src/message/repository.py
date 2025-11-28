import datetime
from typing import Optional, Sequence
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from src.common import AbstractRepository
from .models import Message
from .schemas import MessageRequest
from src.core import logger



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
        try:
            self.session.add(entity)
            await self.session.flush() 
            await self.session.refresh(entity)
            await self.session.commit()
            logger.info(f"message created successfully with ID: {entity.id}")
            return entity
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"DB Error creating message: {e}", exc_info=True)
            raise

    async def get_by_id(self, entity_id: int) -> Optional[Message]:
        """Retrieves a message by its primary key (ID)."""
        stmt = select(Message).where(Message.id == entity_id)
        result = await self.Message.execute(stmt)
        logger.debug(f'Retrieved message by ID {entity_id}')
        return result.scalars().first()

    async def update(self, message_id: int, update_data: dict) -> Optional[Message]:
        """
        Updates fields of an existing Message.
        """
        message_object: Message = await self.get_by_id(message_id)
        if not update_data:
            logger.warning(f"Attempted to update Message ID {message_id} with empty data.")
            return await message_object

        update_data['updated_at'] = datetime.datetime.now() 

        try:
            stmt = (
                update(Message)
                .where(Message.id == message_id)
                .values(**update_data)
                .execution_options(synchronize_session="fetch")
            )
            
            result = await self.session.execute(stmt)
            await self.session.commit() 
            
            if result.rowcount == 0:
                logger.warning(f"Update failed: message ID {message_id} not found.")
                return None
                
            logger.info(f"Message ID {message_id} updated successfully.")
            return await self.get_by_id(message_id)
        
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"DB Error updating Message ID {message_id}: {e}", exc_info=True)
            raise


    async def delete_by_id(self, entity_id: int) -> bool:
        """Deletes a message by ID."""
        try:
            stmt = delete(Message).where(Message.id == entity_id)
            result = await self.session.execute(stmt)
            await self.session.commit() 
            if result.rowcount > 0:
                logger.info(f"Message ID {entity_id} deleted successfully.")
                return True
            return False
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"DB Error deleting Message ID {entity_id}: {e}", exc_info=True)
            raise

    async def get_all(self, session_id: int,  skip: int = 0, limit: int = 100) -> Sequence[Message]:
        """Retrieves a list of messages with pagination. for specfic session"""
        stmt = select(Message).offset(skip).limit(limit).order_by(Message.id).where(Message.session_id == session_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    
    
    async def get_message_conversion_history(self, session_id: int, number_of_messages: int = 2) -> list[dict]:
        """
        retrieve all messages in the database and return as list of dict with role and content keys
        """
        stmt = select(Message.role, Message.content).where(Message.session_id == session_id).order_by(Message.created_at.desc())
        result = await self.session.execute(stmt)
        rows = result.all()[:number_of_messages]
        return [ {"role": r.role, "content": r.content} for r in rows ]
    

