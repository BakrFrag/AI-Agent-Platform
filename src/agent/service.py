from typing import Sequence
from .repository import AgentRepository
from .models import Agent
from .schemas import AgentCreate, AgentUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from src.core import logger
from src.common import AbstractRepository, get_cairo_time, UUID7Str
class AgentService:
    """
    Service layer for Agent business logic, orchestrating Repository calls.
    """
    def __init__(self, repsository: AbstractRepository):
        self.repository = repsository

    async def create_agent(self, agent_data: AgentCreate) -> Agent:
        """Creates a new Agent with basic validation."""
        new_agent = Agent(** agent_data.model_dump())
        agent = await self.repository.create(new_agent)
        logger.info(f"Agent Create {agent}")
        return agent
    
    async def get_agent(self, agent_id: UUID7Str) -> Agent:
        """Retrieves an Agent or raises 404."""
        agent = await self.repository.get_by_id(agent_id)
        if not agent:
            logger.warning(f"Agent ID {agent_id} not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent with ID {agent_id} not found."
            )
        logger.debug(f"Agent with id {agent_id} exist abd returned")
        return agent

    async def update_agent(self, agent_id: UUID7Str, agent_data: AgentUpdate) -> Agent:
        """Updates an Agent, ensuring it exists first."""
        await self.get_agent(agent_id) 
        update_dict = agent_data.model_dump(exclude_none=True)
        if not update_dict:
            logger.error(f"Agent id {agent_id} parsed Agent data {update_dict} not include fields for agent")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve updated agent data."
            )
        update_dict["updated_at"] = get_cairo_time()
        updated_agent = await self.repository.update(agent_id, update_dict)
        logger.info(f"agent id {agent_id} updated with data {update_dict}")
        return updated_agent

    async def delete_agent(self, agent_id: UUID7Str) -> None:
        """Deletes an Agent, raising 404 if it did not exist."""
        deleted = await self.repository.delete_by_id(agent_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent with ID {agent_id} not found."
            )

    async def list_agents(self, skip: int = 0, limit: int = 100) -> Sequence[Agent]:
        """Lists all Agents with pagination."""
        logger.debug(f"list agent with skip {skip} limit {limit}")
        return await self.repository.get_all(skip=skip, limit=limit)