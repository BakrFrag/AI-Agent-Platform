import datetime
from typing import Optional, Sequence
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from src.common import AbstractRepository
from .models import VoiceJob as Job
from .types import VoiceJobStatus
from src.core import logger



class JobRepository(AbstractRepository[VoiceJob, int]):
    """
    Concrete repository for Job Voices entities. 
    Handles all direct, low-level SQLAlchemy interactions for the Job model.
    """

    def __init__(self, session: AsyncSession):
        """Initializes the repository with the active database session."""
        super().__init__(session, Job)

    async def create(self, entity) -> Job:
        """
        Inserts a new Job entity into the database.
        
        Args:
            entity: The Job ORM object to be persisted.
        
        Returns:
            The newly created Job object with generated IDs/timestamps.
        """
        try: 
            self.session.add(entity)
            await self.session.flush() 
            await self.session.refresh(entity)
            await self.session.commit()
            logger.info(f"Job created successfully with ID: {entity.id}")
            return entity
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"DB Error creating Job: {e}", exc_info=True)
            raise

    async def get_by_id(self, entity_id: int) -> Optional[Job]:
        """Retrieves a Job by its primary key (ID)."""
        stmt = select(Job).where(Job.id == entity_id)
        result = await self.Job.execute(stmt)
        logger.debug(f'Retrieved Job by ID {entity_id}')
        return result.scalars().first()

    async def update(self, Job_id: int, update_data: dict) -> Optional[Job]:
        """
        Updates fields of an existing Job.
        """
        Job_object: Job = await self.get_by_id(Job_id)
        if not update_data:
            logger.warning(f"Attempted to update Job ID {Job_id} with empty data.")
            return await Job_object

        update_data['updated_at'] = datetime.datetime.now() 

        try:
            stmt = (
                update(Job)
                .where(Job.id == Job_id)
                .values(**update_data)
                .execution_options(synchronize_session="fetch")
            )
            
            result = await self.session.execute(stmt)
            await self.session.commit() 
            
            if result.rowcount == 0:
                logger.warning(f"Update failed: Job ID {Job_id} not found.")
                return None
                
            logger.info(f"Job ID {Job_id} updated successfully.")
            return await self.get_by_id(Job_id)
        
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"DB Error updating Job ID {Job_id}: {e}", exc_info=True)
            raise


    async def delete_by_id(self, entity_id: K) -> bool:
        pass

    
    async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[M]:
        pass