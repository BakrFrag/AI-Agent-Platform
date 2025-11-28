from typing import Sequence
from io import BytesIO
from .repository import MessageRepository
from .models import Message as MessageModel
from .schemas import Message, MessageRequest, MessageRole, MessageType
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from src.core import logger
from src.llm_interaction.openai_client import AsyncOpenAIClient
from src.session.service import SessionService
from .utils import ensure_valid_audio
class MessageService:
    """
    Service layer for Message business logic, orchestrating Repository calls.
    """
    def __init__(self, session: AsyncSession):
        self.repository = MessageRepository(session)
        self.client = AsyncOpenAIClient()
        self.session_service = SessionService(session)
    def _generate_assistant_message(self, session_id: int, content: str, type: MessageType) -> MessageModel:
        """Creates a new assistant message. save llm responses"""
        message_data = MessageRequest(
            session_id= session_id,
            role=MessageRole.ASSISTANT,
            type=MessageType.TEXT,
            content= content
        )
        return MessageModel(**message_data.model_dump())

    def _generate_user_message(self, session_id: int,type: MessageType, content: str) -> MessageModel:
        """Creates a new user message."""
        message_data = MessageRequest(
            session_id= session_id,
            role=MessageRole.USER,
            type=MessageType.TEXT if type == MessageType.TEXT else MessageType.VOICE,
            content= content
        )
        return MessageModel(**message_data.model_dump())
    
        
    async def _add_message(self, role: MessageRole, kwargs) -> Message:

        """Creates a new message with basic validation."""
        message = self._generate_user_message(** kwargs) if role == MessageRole.USER else self._generate_assistant_message(**kwargs)
        return await self.repository.create(message)


    async def list_session_messages(self,session_id: int, skip: int = 0, limit: int = 100) -> Sequence[Message]:
        """Lists all messages by session id with pagination."""
        return await self.repository.get_all(session_id = session_id, skip=skip, limit=limit)
    
    async def _get_session_object(self, session_id: int):
        """Fetches the session object by ID."""
        return await self.session_service.get_session_by_id(session_id)   
        
    async def _get_conversion_history(self, session_id: int) -> list[dict]:
        """Fetches the conversation history for a session."""

        conversation_history = await self.repository.get_message_conversion_history(session_id)
        return conversation_history

    async def receive_text_message(self, session_id: int, content: str) -> Message:
        """Handles receiving a new message and returns the created message."""
        
        session_object =  await self._get_session_object(session_id)   
        created_message = await self._add_message(MessageRole.USER, {"session_id": session_id, "type":MessageType.TEXT, "content":content})
        agent_prompt = session_object.agent.prompt
        conversation_history = await self._get_conversion_history(session_id)
        ai_content = await self.client.send_text_message(
            session_id = created_message.session_id, 
            content =  created_message.content,
            prompt = agent_prompt, 
            conversation_history= conversation_history
        )
        logger.debug(f"Generated AI text response: {ai_content} for session {session_id}")
        ai_message = await self._add_message(MessageRole.ASSISTANT, {
            "session_id": session_id, 
            "type":MessageType.TEXT, 
            "content":ai_content
        })
        return ai_message
       
    

    async def receive_voice_message(self, session_id: int, voice_note: bytes) -> Message:
        """Handles receiving a new voice note message and returns the created message."""
        session_object =  await self._get_session_object(session_id) 
        if not await ensure_valid_audio(voice_note):
            logger.error(f"Invalid audio file format or corrupted file for session {session_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid audio file format or corupted file."
            )
        logger.debug(f"uploaded file is valid audio for session {session_id}")
       
        llm_stt = await self.client.speech_to_text(
            voice_note = voice_note)
          
        stt_message = await self._add_message(MessageRole.USER , {"session_id": session_id,  "type": MessageType.VOICE, "content": llm_stt})
        logger.debug(f"Transcribed voice note to text: {stt_message}")
        agent_prompt = session_object.agent.prompt
        conversation_history = await self._get_conversion_history(session_id)
        text = await self.client.send_text_message(
            session_id = stt_message.session_id, 
            content =  stt_message.content,
            prompt = agent_prompt, 
            conversation_history= conversation_history
        )
        logger.debug(f"Generated AI text response: {text} and audio response for session {session_id}")
        await self._add_message(MessageRole.ASSISTANT,{"session_id": session_id, "type": MessageType.TEXT, "content": text})
        speech_bytes = await self.client.text_to_speech(
            text = text[:4000],
            voice = "alloy",   
            format = "mp3"  
        )
       
        return speech_bytes