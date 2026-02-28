from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.common.orm_base import Base

class Session(Base):
    """
    Represents a single conversation session between a user and an AI agent.
    
    This model stores metadata about the chat session, but not the individual messages.
    """
    __tablename__ = 'sessions'

    
    title = Column(String, default="New Chat Session")
    agent_id = Column(
        String(36),
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    agent = relationship(
        "Agent",
        back_populates="sessions",
        lazy="joined"  # Eager load agent when loading session
    )

    messages = relationship(
        "Message", 
        back_populates="session",
        cascade="all, delete-orphan",  # If session deleted, delete all messages
        order_by="Message.created_at",  # Always return messages in chronological order
        lazy="selectin"
    )
    
    def __repr__(self):
        return f"<Session(id={self.id}, title='{self.title}', agent_id='{self.agent_id}')>"

