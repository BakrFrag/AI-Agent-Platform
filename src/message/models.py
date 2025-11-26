from sqlalchemy import Column, Integer, String, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from src.common.orm_base import Base
from .types import MessageType, MessageRole
class Message(Base):
    """
    Message - A single message in a conversation
    Each message belongs to one session
    Can be from user or assistant
    Can be text or voice type
    """
    __tablename__ = "messages"


    session_id = Column(
        Integer, 
        ForeignKey("sessions.id", ondelete="CASCADE"),  
        nullable=False,
        index=True  
    )
    role = Column(SQLEnum(MessageRole), nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)  # The actual text content
    type = Column(SQLEnum(MessageType), default=MessageType.TEXT, nullable=False)
    audio_url = Column(String(500), nullable=True)
    
    session = relationship("Session", back_populates="messages")
    
    def __repr__(self):
        return f"<Message(id={self.id}, session_id={self.session_id}, role='{self.role}', type='{self.type}')>"
