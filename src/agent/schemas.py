from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class AgentBase(BaseModel):
    name: str = Field(..., max_length=100)
    prompt: str = Field(..., description="The system prompt defining the agent's persona.")
   

class AgentCreate(AgentBase):
    pass

class AgentUpdate(BaseModel):
    name: Optional[str] = Field(None)
    prompt: Optional[str] = Field(None)
class AgentRead(AgentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True