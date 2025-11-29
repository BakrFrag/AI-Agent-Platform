from typing import List
from fastapi import APIRouter, Depends, status
from .schemas import AgentCreate, AgentRead, AgentUpdate
from .service import AgentService
from .dependency  import get_agent_repository
from .repository import AgentRepository
from src.common import UUID7Str

router = APIRouter(prefix="/agent", tags=["Agents"])

@router.post(
    "/", 
    response_model=AgentRead, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new AI Agent"
)
async def create_agent(
    agent_data: AgentCreate,
    agent_repository: AgentRepository = Depends(get_agent_repository)
):
    """Creates a new AI Agent persona."""
    service = AgentService(agent_repository)
    return await service.create_agent(agent_data)

@router.get(
    "/", 
    response_model=List[AgentRead],
    summary="List all AI Agents"
)
async def list_agents(
    skip: int = 0, 
    limit: int = 100,
    agent_repository: AgentRepository = Depends(get_agent_repository)
):
    """Retrieves a list of all defined AI Agents."""
    service = AgentService(agent_repository)
    return await service.list_agents(skip=skip, limit=limit)

@router.get(
    "/{agent_id}", 
    response_model=AgentRead,
    summary="Get a specific AI Agent by ID"
)
async def get_agent(
    agent_id: UUID7Str,
    agent_repository: AgentRepository = Depends(get_agent_repository)
):
    """Retrieves a single AI Agent's details."""
    service = AgentService(agent_repository)
    return await service.get_agent(agent_id)

@router.put(
    "/{agent_id}",
    response_model=AgentRead,
    summary="Update an existing AI Agent"
)
async def update_agent(
    agent_id: UUID7Str,
    agent_data: AgentUpdate,
    agent_repository: AgentRepository = Depends(get_agent_repository)
):
    """Updates the name, system prompt, or active status of an AI Agent."""
    service = AgentService(agent_repository)
    return await service.update_agent(agent_id, agent_data)

@router.delete(
    "/{agent_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an AI Agent"
)
async def delete_agent(
    agent_id: UUID7Str,
    agent_repository: AgentRepository = Depends(get_agent_repository)
):
    """Deletes an AI Agent."""
    service = AgentService(agent_repository)
    await service.delete_agent(agent_id)
    return 204