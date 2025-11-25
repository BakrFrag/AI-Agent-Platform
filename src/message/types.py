from enum import StrEnum

class MeesageRole(StrEnum):
    """Role of the message sender"""
    USER = "user"       
    ASSISTANT = "assistant"

class MessageType(StrEnum):
    """Type of message: text or voice"""
    TEXT = "text"
    VOICE = "voice"

class VoiceTaskStatus(StrEnum):
    """Status of voice message processing"""
    QUEUED = "queued"
    TRANSCRIBING = "transcribing"
    GENERATING = "generating"
    SYNTHESIZING = "synthesizing"
    COMPLETED = "completed"
    FAILED = "failed"