from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Enum as SqlEnum, String, Text
from .types import VoiceJobStatus
from src.common import Base

class VoiceJob(Base):

    __tablename__ = "voice_jobs"
    
    
    status = Column(SqlEnum(VoiceJobStatus), default= VoiceJobStatus.PENDING)  # PENDING, PROCESSING, COMPLETED, FAILED
    user_audio_path = Column(String)
    voice_to_text = Column(Text, nullable=True)
    ai_text_response = Column(Text, nullable=True)
    ai_spech_audio_path = Column(String, nullable=True)
    
   