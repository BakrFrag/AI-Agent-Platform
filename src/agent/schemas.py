from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class AgentBase(BaseModel):
    name: str = Field(..., max_length=100)
    system_prompt: str = Field(..., description="The system prompt defining the agent's persona.")
   # is_active: bool = Field(True)

class AgentCreate(AgentBase):
    pass

class AgentUpdate(BaseModel):
    pass

class AgentRead(AgentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True