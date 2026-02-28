from typing import List, Optional
from fastapi import HTTPException, status
from src.core import logger
from .schemas import SessionCreate, SessionUpdate, Session
from .models import Session
from src.common import UUID7Str, get_cairo_time, AbstractRepository
class SessionService:
    """
    Handles the business logic for Session resources, coordinating data access
    and applying validation rules.
    """

    def __init__(self, session_repository: AbstractRepository):
        """Initializes the service with repository instances."""
        self.session_repo = session_repository
       
       

    async def create_session(self, session_data: SessionCreate) -> Session:
        """
        create session
        """
        agent = await self.session_repo.get_agent(session_data.agent_id)
        if not agent:
            logger.error(f"Failed to create session: Agent ID {session_data.agent_id} not found.")
            raise HTTPException(status_code=404, detail = f"agent with id {session_data.agent_id} not found")

        session = Session(
            agent_id=session_data.agent_id,
            title=session_data.title,
        )
        created_session = await self.session_repo.create(session)
        logger.debug(f"session object created as {created_session}")
        return created_session
    

    async def get_session_by_id(self, session_id: UUID7Str) -> Session:
        """Retrieves a single session by ID."""
        session = await self.session_repo.get_by_id(session_id)
        if not session:
            logger.error(f"session with id {session_id} not exists")
            raise HTTPException(status_code=404, detail=f"Session with id {session_id} not found"   )
        return session
    
   
    async def update_session(self, session_id: UUID7Str, update_data: SessionUpdate) -> Session:
        """Updates the title or agent related to session of an existing session."""

        session_object = await self.get_session_by_id(session_id)
        update_dict = update_data.model_dump(exclude_none= True)
        if not update_dict:
            logger.warning(f"No update data provided for Session ID {session_id}.")
            return session_object
        agent_id = update_dict.get("agent_id", None)
        if agent_id is not None and (await self.session_repo.get_agent(agent_id)) is None:
                logger.error(f"failed to update session {session_id} parsed agent id {agent_id} is not exists")
                raise HTTPException(
                    status_code= 400, 
                    detail = f"Agent with id {agent_id} not exists"
                )
        update_dict["updated_at"] = get_cairo_time()
        updated_session = await self.session_repo.update(session_id, update_dict)
        logger.info(f"session object with id {session_id} updated with {update_dict}")
        return updated_session
    

    async def delete_session(self, session_id: UUID7Str):
        """Deletes a session by ID."""
        await self.get_session_by_id(session_id)
        logger.debug(f"start delete session object {session_id}")
        await self.session_repo.delete_by_id(session_id)
        
    async def list_sessions(self, skip: int = 0, limit: int = 100) -> List[Session]:
        """Lists all sessions with pagination."""
        
        logger.info(f"list session objects with skip {skip} and limit {limit}")
        sessions = await self.session_repo.get_all(skip=skip, limit=limit)
        return sessions 