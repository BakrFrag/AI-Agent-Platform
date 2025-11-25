from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .schemas import MessageType, MessageRole

class TextMessageRequest(BaseModel):
    message: str = Field(..., min_length=2, max_length=4000)

class MessageResponse(BaseModel):
    id: int
    session_id: int
    role: MessageRole
    content: str
    type: MessageType
    audio_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    """Response containing both user and assistant messages"""
    user_message: MessageResponse
    assistant_message: MessageResponse
    session_id: int