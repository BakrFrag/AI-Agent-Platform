from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .types import MessageType, MessageRole

class MessageRequest(BaseModel):
    content: str = Field(..., min_length=2)
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
    created_at: datetime
    
    class Config:
        from_attributes = True
