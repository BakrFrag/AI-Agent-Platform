from typing import List, Sequence, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
# Placeholder imports from other layers
from src.core.logger import logger
from src.agents.repository import AgentRepository 
from src.agents.exceptions import AgentNotFoundError # Assuming this exists
from .session_repository import SessionRepository, Session # Import ORM model and repository
from .session_dtos import SessionCreate, SessionUpdate, SessionResponse 
from .session_exceptions import (
    SessionNotFoundError, 
    AgentNotAvailableError
)



class SessionService:
    """
    Handles the business logic for Session resources, coordinating data access
    and applying validation rules.
    """

    def __init__(self, db_session: AsyncSession):
        """Initializes the service with repository instances."""
        self.session_repo = SessionRepository(db_session)
        # In a real app, this would be the actual AgentRepository
        self.agent_repo = AgentRepositoryMock(db_session) 

    async def create_session(self, session_data: SessionCreate) -> SessionResponse:
        """
        Validates agent status and creates a new session.
        """
        # 1. Validation: Check if the Agent exists and is active
        agent = await self.agent_repo.get_by_id(session_data.agent_id)
        
        if not agent:
            logger.error(f"Failed to create session: Agent ID {session_data.agent_id} not found.")
            raise HTTPException(status_code=404, detail = f"agent with id {session_data.agent_id} not found")

        session = Session(
            agent_id=session_data.agent_id,
            title=session_data.title,
        )
        created_session = await self.session_repo.create(session)
        return self.get_session_by_id(created_session.id)

    async def get_session_by_id(self, session_id: int) -> SessionResponse:
        """Retrieves a single session by ID."""
        session = await self.session_repo.get_by_id(session_id)
        if not session:
            raise SessionNotFoundError(session_id)
        return SessionResponse.from_model(session)

    async def get_sessions_by_user(self, user_id: str, skip: int = 0, limit: int = 100) -> List[SessionResponse]:
        """Retrieves all sessions for a specific user."""
        sessions = await self.session_repo.get_by_user_id(user_id, skip, limit)
        return [SessionResponse.from_model(s) for s in sessions]

    async def update_session(self, session_id: int, update_data: SessionUpdate) -> SessionResponse:
        """Updates the title or status of an existing session."""
        update_dict = update_data.to_update_dict()
        
        if not update_dict:
            # Nothing to update, just return the current state
            return await self.get_session_by_id(session_id)

        updated_session = await self.session_repo.update(session_id, update_dict)
        
        if not updated_session:
            raise SessionNotFoundError(session_id)

        return SessionResponse.from_model(updated_session)

    async def delete_session(self, session_id: int) -> bool:
        """Deletes a session by ID."""
        success = await self.session_repo.delete_by_id(session_id)
        if not success:
            raise SessionNotFoundError(session_id)
        return success