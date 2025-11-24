from typing import Optional, Dict, Any, List
from pydantic import BaseModel
import datetime

class SessionBase(BaseModel):
   
    agent_id: int
    title: Optional[str] = "New Chat Session"
    

class SessionCreate(SessionBase):
    """Schema for initiating a new chat session."""
    pass
   
    
class SessionUpdate(BaseModel):
    """Schema for updating an existing Session (e.g., changing the title or status)."""
    title: Optional[str] = None
    agent_id: Optional[int] = None  
    def to_update_dict(self) -> Dict[str, Any]:
        """Returns a dictionary with only non-None values for database update."""
        return self.model_dump(exclude_none=True)

class SessionResponse(BaseModel):
    """Schema for returning Session data to the client."""
    id: int
    agent_id: int
    title: Optional[str] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

