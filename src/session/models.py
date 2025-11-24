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

    
    title = Column(String, default="New Chat Session")
    agent_id = Column(
        Integer,
        ForeignKey("agent.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    agent = relationship(
        "Agent",
        back_populates="sessions",
    )
    
    def __repr__(self):
        return f"<Session(id={self.id}, title='{self.title}', agent_id='{self.agent_id}')>"

