from typing import List
from fastapi import APIRouter, Depends, status, File, UploadFile
from fastapi.responses import FileResponse
from .schemas import MessageRequest, Message, ConversationResponse
from .dependency  import get_message_service
from .service import MessageService


router = APIRouter(prefix="/message", tags=["Messages"])

@router.post(
    "/message/text", 
    response_model=Message, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Message"
)
async def receive_text_message(
    message_data: MessageRequest,
    service: MessageService = Depends(get_message_service)
):
    """Creates a new message"""
    return await service.receive_message(message_data)

@router.post(
    "/message/voice", 
    response_model=Message, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Message voice note"
)
async def receive_voice_message(
    session_id: int,
    voice_note:UploadFile =  File(),
    service: MessageService = Depends(get_message_service)
):
    """Creates a new message"""

    return await service.receive_voice_message(session_id, voice_note)


@router.get(
    "/conversation/{session_id}", 
    response_model=List[Message],
    summary="List all AI Messages within session"
)
async def list_messages_within_session(
    session_id: int,
    skip: int = 0, 
    limit: int = 100,
    service: MessageService = Depends(get_message_service)
):
    """Retrieves a list of all defined AI Agents."""
    return await service.list_session_messages(session_id= session_id, skip=skip, limit=limit)

