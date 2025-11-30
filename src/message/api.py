from typing import List
from fastapi import APIRouter, Depends, status, File, UploadFile, Form
from fastapi.responses import Response
from src.common import AbstractRepository, UUID7Str
from .schemas import MessageRequest, Message
from .dependency  import get_message_repository
from .service import MessageService


message_router = APIRouter(prefix="/message", tags=["Messages"])

@message_router.post(
    "/text", 
    response_model=Message, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Message"
)
async def receive_text_message(
    message_data: MessageRequest,
    repository: AbstractRepository = Depends(get_message_repository)
):
    """Creates a new message"""
    service: MessageService = MessageService(repository)
    return await service.receive_text_message(message_data.session_id, message_data.content)

@message_router.post(
    "/voice", 
    response_model=Message, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Message voice note"
)
async def receive_voice_message(
    session_id: UUID7Str  = Form(...),
    voice_note:UploadFile =  File(),
    repository: AbstractRepository = Depends(get_message_repository)
):
    """Creates a new message"""
    voice_note_bytes = await voice_note.read()
    service: MessageService = MessageService(repository)

    voice_file = await service.receive_voice_message(session_id, voice_note_bytes)
    return Response(
        content=voice_file,
        media_type="audio/mpeg",  # for mp3
        headers={
            "Content-Disposition": 'inline; filename="speech.mp3"'
        },
    )


@message_router.get(
    "/conversation/{session_id}", 
    response_model=List[Message],
    summary="List all AI Messages within session"
)
async def list_messages_within_session(
    session_id: UUID7Str,
    skip: int = 0, 
    limit: int = 100,
    repository: AbstractRepository = Depends(get_message_repository)
    
):
    """Retrieves a list of all defined AI Agents."""
    service: MessageService = MessageService(repository)
    return await service.list_session_messages(session_id= session_id, skip=skip, limit=limit)

