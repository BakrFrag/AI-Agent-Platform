from typing import Sequence, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.common import AbstractRepository
from .models import Agent
from src.core import logger

class AgentRepository(AbstractRepository[Agent, int]):
    """
    Concrete repository for Agent. All methods are fully async.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(session, Agent)

    async def create(self, entity: Agent) -> Agent:
        """Adds a new Agent and loads the generated ID."""
        self.session.add(entity)
        await self.session.flush() 
        await self.session.refresh(entity)
        await self.session.commit()
        logger.debug(f"Created new agent with ID: {entity.id}")
        return entity

    async def get_by_id(self, entity_id: int) -> Optional[Agent]:
        """Retrieves an Agent by ID."""
        stmt = select(Agent).where(Agent.id == entity_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def update(self, agent_id: int, update_data: dict) -> Optional[Agent]:
        """Updates an existing Agent using the bulk update pattern."""
        
        if not update_data:
            logger.warning(f"Attempted to update Agent ID {agent_id} with empty data.")
            return await self.get_by_id(agent_id) 
        stmt = (
            update(Agent)
            .where(Agent.id == agent_id)
            .values(**update_data)
        )
        
        await self.session.execute(stmt)
        await self.session.commit() 
        logger.debug(f"Updated Agent ID: {agent_id}")
        
        # Must fetch the updated object to reflect the changes (e.g., updated_at)
        return await self.get_by_id(agent_id)

    async def delete_by_id(self, entity_id: int) -> bool:
        """Deletes an Agent by ID."""
        stmt = delete(Agent).where(Agent.id == entity_id)
        result = await self.session.execute(stmt)
        await self.session.commit() 
        if result.rowcount > 0:
            logger.info(f"Deleted Agent ID: {entity_id}")
            return True
        return False

    async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[Agent]:
        """Retrieves a list of Agents with pagination."""
        stmt = select(Agent).offset(skip).limit(limit).order_by(Agent.id)
        result = await self.session.execute(stmt)
        return result.scalars().all()