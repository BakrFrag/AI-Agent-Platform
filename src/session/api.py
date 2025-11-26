from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import (
    SessionCreate,
    SessionUpdate,
    Session
)
from .dependancy import get_session_service
from .service import SessionService
router = APIRouter(prefix="/session",tags=["Sessions"])



@router.post(
    "/", 
    response_model=Session, 
    status_code=status.HTTP_201_CREATED, 
    summary="Create a new chat session"
)
async def create_session(
    request: SessionCreate,
    service: SessionService = Depends(get_session_service)
):
    """
    Creates a new chat session linked to a specific AI agent.
    """
   
    session = await service.create_session(request)
    return session
   

@router.get(
    "/{session_id}", 
    response_model=Session, 
    summary="Get session metadata by ID"
)
async def get_session(
    session_id: int, 
    service: SessionService = Depends(get_session_service)
):
    """
    Retrieves the metadata for a specific chat session.
    """
    session = await service.get_session_by_id(session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return session


@router.get(
    "/", 
    response_model=List[Session], 
    summary="List all active chat sessions"
)
async def list_sessions(
     skip: int = 0, 
    limit: int = 100,
    service: SessionService = Depends(get_session_service)):
    """
    Retrieves a list of all chat sessions for the current user (simulated).
    """
    return await service.list_sessions(skip = skip, limit = limit)


@router.patch(
    "/{session_id}", 
    response_model=Session, 
    summary="Update session title"
)
async def update_session(
    session_id: int,
    request: SessionUpdate,
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
    We return 204 even if not found, as the desired state (deleted) is achieved (Idempotence)
    """
    await service.delete_session(session_id)
    return 204