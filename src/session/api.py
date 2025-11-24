from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
# Mocking the dependency injection of the DB session
from sqlalchemy.ext.asyncio import AsyncSession
# Assume a utility function to get the session
def get_db_session() -> AsyncSession:
    """Dependency: Simulates getting an active DB session."""
    # This would yield a session from a connection pool in a real FastAPI app
    raise NotImplementedError("Database dependency not implemented in this mock.")

# Import the service and schemas we defined
from session_service import SessionService, SessionCreateRequest, SessionUpdateRequest, SessionResponse, SessionServiceError

# Create the router for /sessions
router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"],
    responses={404: {"description": "Not found"}},
)

# Dependency injection for the SessionService
def get_session_service(db: AsyncSession = Depends(get_db_session)) -> SessionService:
    """Dependency: Provides an instance of the SessionService."""
    return SessionService(db)


@router.post(
    "/", 
    response_model=SessionResponse, 
    status_code=status.HTTP_201_CREATED, 
    summary="Create a new chat session"
)
async def create_session(
    request: SessionCreateRequest,
    service: SessionService = Depends(get_session_service)
):
    """
    Creates a new chat session linked to a specific AI agent.
    """
    try:
        session = await service.create_new_session(request)
        return session
    except SessionServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/{session_id}", 
    response_model=SessionResponse, 
    summary="Get session metadata by ID"
)
async def get_session(
    session_id: int, 
    service: SessionService = Depends(get_session_service)
):
    """
    Retrieves the metadata for a specific chat session.
    """
    session = await service.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return session


@router.get(
    "/", 
    response_model=List[SessionResponse], 
    summary="List all active chat sessions"
)
async def list_sessions(service: SessionService = Depends(get_session_service)):
    """
    Retrieves a list of all chat sessions for the current user (simulated).
    """
    return await service.get_sessions_list()


@router.patch(
    "/{session_id}", 
    response_model=SessionResponse, 
    summary="Update session title"
)
async def update_session(
    session_id: int,
    request: SessionUpdateRequest,
    service: SessionService = Depends(get_session_service)
):
    """
    Updates mutable session properties, such as the user-friendly title.
    """
    updated_session = await service.update_session(session_id, request)
    if updated_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return updated_session


@router.delete(
    "/{session_id}", 
    status_code=status.HTTP_204_NO_CONTENT, 
    summary="Delete a chat session"
)
async def delete_session(
    session_id: int, 
    service: SessionService = Depends(get_session_service)
):
    """
    Deletes the session and all associated messages.
    """
    if not await service.delete_session_by_id(session_id):
        # We return 204 even if not found, as the desired state (deleted) is achieved (Idempotence)
        # However, for user feedback, a 404 is often more useful here.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return