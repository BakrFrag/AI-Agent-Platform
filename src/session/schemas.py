from typing import Optional, Dict, Any, List
from pydantic import BaseModel
import datetime
from src.common import UUID7Str
class SessionBase(BaseModel):
   
    agent_id: UUID7Str
    title: Optional[str] = "New Chat Session"
    

class SessionCreate(SessionBase):
    """Schema for initiating a new chat session."""
    pass
   
    
class SessionUpdate(BaseModel):
    """Schema for updating an existing Session (e.g., changing the title or status)."""
    title: Optional[str] = None
    agent_id: Optional[UUID7Str] = None  
    def to_update_dict(self) -> Dict[str, Any]:
        """Returns a dictionary with only non-None values for database update."""
        return self.model_dump(exclude_none=True)

class Session(SessionBase):
    """Schema for returning Session data to the client."""
    id: UUID7Str
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None

