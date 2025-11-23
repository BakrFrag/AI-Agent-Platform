from typing import Sequence
from .repository import AgentRepository
from .models import Agent
from .schemas import AgentCreate, AgentUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from src.core import logger

class AgentService:
    """
    Service layer for Agent business logic, orchestrating Repository calls.
    """
    def __init__(self, session: AsyncSession):
        self.repository = AgentRepository(session)
    
    
    async def create_agent(self, agent_data: AgentCreate) -> Agent:
        """Creates a new Agent with basic validation."""
        # Simple Business Rule Example
        if not agent_data.system_prompt.strip():
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="System prompt cannot be empty."
            )
        
        new_agent = Agent(**agent_data.model_dump())
        return await self.repository.create(new_agent)

    async def get_agent(self, agent_id: int) -> Agent:
        """Retrieves an Agent or raises 404."""
        agent = await self.repository.get_by_id(agent_id)
        if not agent:
            logger.warning(f"Agent ID {agent_id} not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent with ID {agent_id} not found."
            )
        return agent

    async def update_agent(self, agent_id: int, agent_data: AgentUpdate) -> Agent:
        """Updates an Agent, ensuring it exists first."""
        await self.get_agent(agent_id) 
        update_dict = agent_data.model_dump(exclude_none=True)
        if not update_dict:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update."
            )
        updated_agent = await self.repository.update(agent_id, update_dict)
        if not updated_agent:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve updated agent data."
            )
        return updated_agent

    async def delete_agent(self, agent_id: int) -> None:
        """Deletes an Agent, raising 404 if it did not exist."""
        deleted = await self.repository.delete_by_id(agent_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent with ID {agent_id} not found."
            )

    async def list_agents(self, skip: int = 0, limit: int = 100) -> Sequence[Agent]:
        """Lists all Agents with pagination."""
        return await self.repository.get_all(skip=skip, limit=limit)