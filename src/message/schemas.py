from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .types import MessageType, MessageRole

class MessageRequest(BaseModel):
    content: str = Field(..., min_length=2, max_length=4000)
    session_id: int
    role:  MessageRole = MessageRole.USER
    type: MessageType = MessageType.TEXT
    class Config:
        from_attributes = True
    
class Message(BaseModel):
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
    user_message: Message
    assistant_message: Message
    session_id: int