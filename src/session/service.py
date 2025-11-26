from typing import List, Sequence, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from src.core import logger
from src.agent.service import AgentService
from .schemas import SessionCreate, SessionUpdate, Session
from .repository import SessionRepository
from .models import Session

class SessionService:
    """
    Handles the business logic for Session resources, coordinating data access
    and applying validation rules.
    """

    def __init__(self, db_session: AsyncSession):
        """Initializes the service with repository instances."""
        self.session_repo = SessionRepository(db_session)
        self.agent_repo = AgentService(db_session)
       

    async def create_session(self, session_data: SessionCreate) -> Session:
        """
        create session
        """
        agent = await self.agent_repo.get_agent(session_data.agent_id)
        if not agent:
            logger.error(f"Failed to create session: Agent ID {session_data.agent_id} not found.")
            raise HTTPException(status_code=404, detail = f"agent with id {session_data.agent_id} not found")

        session = Session(
            agent_id=session_data.agent_id,
            title=session_data.title,
        )
        created_session = await self.session_repo.create(session)
        return await self.get_session_by_id(created_session.id)

    async def get_session_by_id(self, session_id: int) -> Session:
        """Retrieves a single session by ID."""
        session = await self.session_repo.get_by_id(session_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"Session with id {session_id} not found"   )
        return session
    
   
    async def update_session(self, session_id: int, update_data: SessionUpdate) -> Session:
        """Updates the title or agent related to session of an existing session."""

        session_object = await self.get_session_by_id(session_id)
        update_dict = update_data.model_dump(exclude_none= True)
        if not update_dict:
            logger.warning(f"No update data provided for Session ID {session_id}.")
            return session_object
        if update_dict.get("agent_id", None) is not None:
            await self.agent_repo.get_agent(update_data.agent_id)
        updated_session = await self.session_repo.update(session_id, update_dict)
        return updated_session
    

    async def delete_session(self, session_id: int):
        """Deletes a session by ID."""
        await self.session_repo.delete_by_id(session_id)
        
    async def list_sessions(self, skip: int = 0, limit: int = 100) -> List[Session]:
        """Lists all sessions with pagination."""
        sessions = await self.session_repo.get_all(skip=skip, limit=limit)
        return sessions 