from typing import List, Optional
from session_repository import SessionRepository
from session_model import Session
from sqlalchemy.ext.asyncio import AsyncSession


class SessionCreateRequest:
    """Represents the data needed to create a session."""
    def __init__(self, agent_id: str):
        self.agent_id = agent_id

class SessionUpdateRequest:
    """Represents the data for updating a session."""
    def __init__(self, title: Optional[str] = None):
        self.title = title

class SessionResponse:
    """Represents the data returned to the client."""
    def __init__(self, session: Session):
        self.id = session.id
        self.agent_id = session.agent_id
        self.title = session.title
        self.status = session.status
        self.created_at = session.created_at
        self.updated_at = session.updated_at
        
class SessionServiceError(Exception):
    """Custom exception for service-level errors."""
    pass
# -----------------------------------------------------------------


class SessionService:
    """
    Handles the business logic related to sessions. 
    It interacts with the repository and applies validation/rules.
    """

    def __init__(self, db_session: AsyncSession):
        self.repository = SessionRepository(db_session)
        # Note: In a real app, you'd inject dependencies like UserService, AgentService here

    async def create_new_session(self, request: SessionCreateRequest) -> SessionResponse:
        """
        Validates the request and calls the repository to create the session.
        """
        if not request.agent_id:
            raise SessionServiceError("Agent ID is required to start a session.")
        
        # In a real scenario, check if the agent_id actually exists in the AgentService
        # if not await self.agent_service.is_valid_agent(request.agent_id):
        #     raise SessionServiceError("Invalid Agent ID provided.")

        session_model = await self.repository.create_session(agent_id=request.agent_id)
        
        # Return the Pydantic-like response object
        return SessionResponse(session_model)

    async def get_session(self, session_id: int) -> Optional[SessionResponse]:
        """Fetches a session by ID and converts it to the response format."""
        session_model = await self.repository.get_session_by_id(session_id)
        if session_model:
            return SessionResponse(session_model)
        return None

    async def get_sessions_list(self) -> List[SessionResponse]:
        """Fetches all sessions (simulating a user's session list)."""
        session_models = await self.repository.get_all_sessions(limit=50)
        return [SessionResponse(s) for s in session_models]

    async def update_session(self, session_id: int, request: SessionUpdateRequest) -> Optional[SessionResponse]:
        """Updates session fields based on the request."""
        if request.title:
            session_model = await self.repository.update_session_title(session_id, request.title)
            if session_model:
                return SessionResponse(session_model)
        
        # If no update occurred or session not found
        return await self.get_session(session_id)

    async def delete_session_by_id(self, session_id: int) -> bool:
        """Marks a session as deleted."""
        # In a production app, you would also handle cascading deletion of all associated messages.
        is_deleted = await self.repository.delete_session(session_id)
        return is_deleted