from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import (
    SessionCreate,
    SessionUpdate,
    Session
)
from src.common import UUID7Str, AbstractRepository
from .dependancy import get_session_repository
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
    session_repository: AbstractRepository = Depends(get_session_repository), 
):
    """
    Creates a new chat session linked to a specific AI agent.
    """
    service: SessionService = SessionService(session_repository)
    return await service.create_session(request)
    
   

@router.get(
    "/{session_id}", 
    response_model=Session, 
    summary="Get session metadata by ID"
)
async def get_session(
    session_id: UUID7Str, 
    repository: AbstractRepository = Depends(get_session_repository)
):
    """
    Retrieves the metadata for a specific chat session.
    """
    service: SessionService = SessionService(repository)
    return await service.get_session_by_id(session_id)


@router.get(
    "/", 
    response_model=List[Session], 
    summary="List all active chat sessions"
)
async def list_sessions(
    skip: int = 0, 
    limit: int = 100,
    repository: AbstractRepository = Depends(get_session_repository)):
    """
    Retrieves a list of all chat sessions for the current user (simulated).
    """
    service: SessionService = SessionService(repository)
    return await service.list_sessions(skip, limit)


@router.put(
    "/{session_id}", 
    response_model=Session, 
    summary="Update session title"
)
async def update_session(
    session_id: UUID7Str,
    session_update: SessionUpdate,
    session_repository: AbstractRepository = Depends(get_session_repository), ):
    """
    Updates mutable session properties, such as the user-friendly title.
    """
    
    service: SessionService = SessionService(session_repository)
    return await service.update_session(session_id, session_update)


@router.delete(
    "/{session_id}", 
    status_code=status.HTTP_204_NO_CONTENT, 
    summary="Delete a chat session"
)
async def delete_session(
    session_id: UUID7Str, 
    repository: AbstractRepository = Depends(get_session_repository)):
    """
    Deletes the session and all associated messages.
    """
    service: SessionService = SessionService(repository)
    return await service.delete_session(session_id)