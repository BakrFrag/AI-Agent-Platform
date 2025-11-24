import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from src.common.orm_base import Base

class Session(Base):
    """
    Represents a single conversation session between a user and an AI agent.
    
    This model stores metadata about the chat session, but not the individual messages.
    """
    __tablename__ = 'sessions'

    agent_id = Column(String, nullable=False, index=True) 
    title = Column(String, default="New Chat Session")
    
    # Relationship to the Message model (for reference, though Message logic is separate)
    # lazy='joined' ensures messages are loaded with the session if needed later.
    # messages = relationship("Message", back_populates="session", lazy="joined")
    
    def __repr__(self):
        return f"<Session(id={self.id}, title='{self.title}', agent_id='{self.agent_id}')>"

