from typing import List
from fastapi import APIRouter, Depends, status
from .schemas import AgentCreate, AgentRead, AgentUpdate
from .service import AgentService
from .dependency  import get_agent_service


agent_router = APIRouter(prefix="/agent", tags=["Agents"])

@agent_router.post(
    "/", 
    response_model=AgentRead, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new AI Agent"
)
async def create_agent(
    agent_data: AgentCreate,
    service: AgentService = Depends(get_agent_service)
):
    """Creates a new AI Agent persona."""
    return await service.create_agent(agent_data)

@agent_router.get(
    "/", 
    response_model=List[AgentRead],
    summary="List all AI Agents"
)
async def list_agents(
    skip: int = 0, 
    limit: int = 100,
    service: AgentService = Depends(get_agent_service)
):
    """Retrieves a list of all defined AI Agents."""
    return await service.list_agents(skip=skip, limit=limit)

@agent_router.get(
    "/{agent_id}", 
    response_model=AgentRead,
    summary="Get a specific AI Agent by ID"
)
async def get_agent(
    agent_id: int,
    service: AgentService = Depends(get_agent_service)
):
    """Retrieves a single AI Agent's details."""
    return await service.get_agent(agent_id)

@agent_router.put(
    "/{agent_id}",
    response_model=AgentRead,
    summary="Update an existing AI Agent"
)
async def update_agent(
    agent_id: int,
    agent_data: AgentUpdate,
    service: AgentService = Depends(get_agent_service)
):
    """Updates the name, system prompt, or active status of an AI Agent."""
    print("model dump:", agent_data.model_dump())
    return await service.update_agent(agent_id, agent_data)

@agent_router.delete(
    "/{agent_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an AI Agent"
)
async def delete_agent(
    agent_id: int,
    service: AgentService = Depends(get_agent_service)
):
    """Deletes an AI Agent."""
    await service.delete_agent(agent_id)
    return 