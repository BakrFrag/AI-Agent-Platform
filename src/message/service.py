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
    
    def _generate_assistant_message(self, session_id: int, ai_response_content: str) -> MessageModel:
        """Creates a new assistant message. save llm responses"""
        message_data = MessageRequest(
            session_id= session_id,
            role=MessageRole.ASSISTANT,
            type=MessageType.TEXT,
            content= ai_response_content
        )
        return MessageModel(**message_data.model_dump())

    def _generate_user_message(self, session_id: int, message_type: MessageType, user_query: str) -> MessageModel:
        """Creates a new user message."""
        message_data = MessageRequest(
            session_id= session_id,
            role=MessageRole.USER,
            type=MessageType.TEXT if message_type == MessageType.TEXT else MessageType.VOICE,
            content= user_query
        )
        return MessageModel(**message_data.model_dump())
    
        
    async def _add_message(self, role: MessageRole, **kwargs) -> Message:

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

    async def receive_text_message(self, message_data: MessageRequest) -> Message:
        """Handles receiving a new message and returns the created message."""
        session_id = message_data.session_id
        session_object =  await self._get_session_object(session_id)   
        created_message = await self._add_message(message_data.role, **message_data.model_dump())
        agent_prompt = session_object.agent.prompt
        conversation_history = await self._get_conversion_history(session_id)
        ai_content = await self.client.send_text_message(
            session_id = created_message.session_id, 
            content =  created_message.content,
            prompt = agent_prompt, 
            conversation_history= conversation_history
        )
        ai_message_data = MessageRequest(
                session_id=created_message.session_id,
                role=MessageRole.ASSISTANT,
                type=MessageType.TEXT,
                content=ai_content
            )
        ai_message = await self._add_message(ai_message_data)
        return ai_message
    

    async def receive_voice_message(self, session_id: int, voice_note: bytes) -> Message:
        """Handles receiving a new voice note message and returns the created message."""
        session_object =  await self._get_session_object(session_id) 
        if not await ensure_valid_audio(voice_note):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid audio file format or corupted file."
            )
        voice_note_file_object = BytesIO(voice_note)
        llm_stt = await self.client.speech_to_text(
            audio_data= voice_note_file_object,
            model="whisper-1")
        # getting the text equvlant to voice note and saving as user message
        stt_message = await self._add_message({"session_id": session_id, "role": MessageRole.USER, "type": MessageType.VOICE, "content": llm_stt.text})
        self.logger.debug(f"Transcribed voice note to text: {stt_message}")
        # now getting AI response to the transcribed text
        agent_prompt = session_object.agent.prompt
        conversation_history = await self._get_conversion_history(session_id)
        text, speech = await self.client.send_text_with_tts(
            session_id = stt_message.session_id, 
            content =  stt_message.content,
            prompt = agent_prompt, 
            conversation_history= conversation_history
        )
        logger.debug(f"Generated AI text response: {text} and audio response of length {len(speech)} bytes for session {session_id}")
        self._add_message({"session_id": session_id, "role": MessageRole.ASSISTANT, "type": MessageType.TEXT, "content": text})
        return speech
        