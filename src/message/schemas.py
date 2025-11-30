from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .types import MessageType, MessageRole
from src.common import UUID7Str
class MessageRequest(BaseModel):
    content: str = Field(..., min_length=2)
    session_id: UUID7Str
    class Config:
        from_attributes = True
    
class Message(BaseModel):
    id: UUID7Str
    session_id: UUID7Str
    role: MessageRole
    content: str
    type: MessageType
    created_at: datetime
    
    class Config:
        from_attributes = True
