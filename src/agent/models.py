from sqlalchemy import Column, String, Text, Boolean
from src.common.orm_base import Base

class Agent(Base):
    """
    SQLAlchemy ORM Model for an AI Agent's definition.
    """
    name = Column(String(100), index=True, nullable=False)
    prompt = Column(Text, nullable=False)
    #is_active = Column(Boolean, default=True, nullable=False)