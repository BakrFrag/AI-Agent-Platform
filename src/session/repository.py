import datetime
from typing import Sequence, Optional
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from src.common import AbstractRepository
from .models import Session
from src.core import logger



class SessionRepository(AbstractRepository[Session, int]):
    """
    Concrete repository for Session entities. 
    Handles all direct, low-level SQLAlchemy interactions for the Session model.
    """

    def __init__(self, session: AsyncSession):
        """Initializes the repository with the active database session."""
        super().__init__(session, Session)

    async def create(self, entity: Session) -> Session:
        """
        Inserts a new Session entity into the database.
        
        Args:
            entity: The Session ORM object to be persisted.
        
        Returns:
            The newly created Session object with generated IDs/timestamps.
        """
        
        self.session.add(entity)
        await self.session.flush() 
        await self.session.refresh(entity)
        await self.session.commit()
        logger.info(f"Session created successfully with ID: {entity.id}")
        return entity
        

    async def get_by_id(self, entity_id: int) -> Optional[Session]:
        """Retrieves a Session by its primary key (ID)."""
        stmt = select(Session).where(Session.id == entity_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def update(self, session_id: int, update_data: dict) -> Optional[Session]:
        """
        Updates fields of an existing Session.
        """
        if not update_data:
            logger.warning(f"Attempted to update Session ID {session_id} with empty data.")
            return await self.get_by_id(session_id) 

        update_data['updated_at'] = datetime.datetime.now() 
        stmt = (
            update(Session)
            .where(Session.id == session_id)
            .values(**update_data)
            .execution_options(synchronize_session="fetch")
        )
        
        result = await self.session.execute(stmt)
        await self.session.commit() 
        
        if result.rowcount == 0:
            logger.warning(f"Update failed: Session ID {session_id} not found.")
            return None
        logger.info(f"Session ID {session_id} updated successfully.")
        return await self.get_by_id(session_id)
        

    async def delete_by_id(self, entity_id: int) -> bool:
        """Deletes a Session by ID."""
        stmt = delete(Session).where(Session.id == entity_id)
        result = await self.session.execute(stmt)
        await self.session.commit() 
        if result.rowcount > 0:
            logger.info(f"Session ID {entity_id} deleted successfully.")
            return True
        return False
        
    async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[Session]:
        """Retrieves a list of Agents with pagination."""
        stmt = select(Session).offset(skip).limit(limit).order_by(Session.id)
        result = await self.session.execute(stmt)
        return result.scalars().all()