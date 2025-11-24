from sqlalchemy import Column, String, Text, Boolean
from sqlalchemy.orm import relationship
from src.common.orm_base import Base

class Agent(Base):
    """
    SQLAlchemy ORM Model for an AI Agent's definition.
    """
    __tablename__ = "agents"
    name = Column(String(100), index=True, nullable=False)
    prompt = Column(Text, nullable=False)
     
    sessions = relationship(
        "Session",
        back_populates="agent",
        cascade="all, delete-orphan",  # delete sessions when agent deleted (optional)
        lazy="selectin",               # to eager loading sessions with the agent
    )

    def __repr__(self):
        return f"<Agent(id={self.id}, name='{self.name}'>"
