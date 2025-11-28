import base64
from io import BytesIO 
from pathlib import Path
from typing import Optional, Tuple
from openai import AsyncOpenAI
from src.core import settings, logger


OPEN_API_API_KEY = settings.OPENAI_API_KEY


class AsyncOpenAIClient:
    """
    Async wrapper around OpenAI for:
      - text -> text conversation
      - text -> audio (TTS)
      - audio -> text (STT)

    Usage:
        client = OpenAIChatAndVoiceClient()

        text = await client.send_text_message("Hello!")
        audio_path = await client.text_to_speech("Hi there", "output.wav")
        transcript = await client.speech_to_text("input.wav")
    """

    def __init__(
        self,
        text_model: str = "gpt-5.1",
        tts_model: str = "gpt-4o-mini-tts",  
        stt_model: str = "gpt-4o-mini-audio",
        max_retries: int = 3,
        base_retry_delay: float = 0.5
    ) -> None:
        self.api_key = OPEN_API_API_KEY
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.text_model = text_model
        self.tts_model = tts_model
        self.stt_model = stt_model
        self.max_retries = max_retries
        self.base_retry_delay = base_retry_delay
        logger.info("Initialized OpenAIChatAndVoiceClient")
    
    async def _generate_llm_input(
        self, user_message: str, session_id: int,
        prompt: Optional[str] = None, conversation_history: Optional[list[dict]] = {}, 
    ) -> list[dict]:
        """
        Generate the input message list for LLM from prompt, history, and user message.
        """
        messages: list[dict] = []
        if prompt:
            messages.append({"role": "system", "content": prompt})
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})
        logger.debug(f"Generated LLM input messages for session {session_id}: {messages}")
        return messages
    

    async def send_text_message(
        self,
        content: str,
        session_id: int,
        prompt: Optional[str] = "",
        conversation_history: Optional[list[dict]] =[],
    ) -> str:
        """
        Send a user message and get a text response.

        content: user message
        prompt: optional system instruction
        conversation_history: previous messages, e.g.
            [
                {"role": "user", "content": "Hi"},
                {"role": "assistant", "content": "Hello!"}
            ]
        :return: assistant response text
        """
        messages = await self._generate_llm_input(
            user_message=content,session_id=session_id,
            prompt=prompt, conversation_history=conversation_history)
        logger.debug(f"Sending message to OpenAI: {content} within session {session_id} and system prompt: {prompt} including {len(conversation_history) if conversation_history else 0} previous messages")
        response = await self.client.responses.create(
            model=self.text_model,
            input = messages
        )
        logger.debug(f"Received response from OpenAI for message {content} within session {session_id}: {response}")
        return response.output_text 

    
    async def text_to_speech(
        self,
        text: str,
        voice: str = "alloy",   
        format: str = "wav",   
    ) -> bytes:
        """
        Convert text to speech and save to `output_path`.
        Args:
            text: text to synthesize
            voice: voice name (depends on the model)
            format: output audio format (e.g. 'mp3', 'wav')
        Returns: 
            Bytes of the synthesized audio file.
        """

        voice = BytesIO.read(text)
        result = await self.client.audio.speech.create(
            model=self.tts_model,
            voice=voice,
            input=text,
            format=format,
        )
        audio_data_b64 = getattr(result, "audio", None) or result.get("audio")  
        audio_bytes = base64.b64decode(audio_data_b64)
        logger.debug(f"TTS generated audio bytes length: {len(audio_bytes)} for text: {text!r}")
        return audio_bytes
    
    async def speech_to_text(
        self,
        voice_note: bytes,
        prompt: Optional[str] = None,
        language: Optional[str] = None,
    ) -> str:
        """
        Transcribe speech from a local audio file to text.
        Args:
            audio_path: path to an audio file (wav, mp3, m4a, etc.)
            prompt: optional transcription hint
            language: optional language hint (e.g. 'en', 'ar')
        Returns:
            transcript text
        """
        voice_note = BytesIO.read(voice_note)
        transcription = await self.client.audio.transcriptions.create(
            model=self.stt_model,
            file= voice_note,
            prompt=prompt,
            language=language,
        )

        transcript = getattr(transcription, "text", None) or transcription.get("text")
        logger.debug(f"STT transcript: {transcript!r}")
        return transcript
    


    async def _parse_responses_tts_output(
        self,
        session_id: int,
        resp: object
    ) -> Tuple[str, bytes]: 
        text_chunks: list[str] = []
        audio_b64: Optional[str] = None

        for block in getattr(resp, "output", []):
            block_type = getattr(block, "type", None)
            if block_type == "output_text":
                for c in getattr(block, "content", []):
                    if getattr(c, "type", None) == "output_text":
                        text_chunks.append(getattr(c, "text", ""))

            elif block_type == "output_audio":
                for c in getattr(block, "content", []):
                    if getattr(c, "type", None) == "output_audio":
                        audio_b64 = getattr(c, "audio", None)

        reply_text = "".join(text_chunks).strip()

        if not reply_text:
            logger.warning("No text found in Responses output")
        if not audio_b64:
            logger.warning("No audio found in Responses output")

        reply_audio_bytes = base64.b64decode(audio_b64) if audio_b64 else b""

        logger.debug(
            f"[session={session_id}] Got reply text length={len(reply_text)}, "
            f"audio bytes={len(reply_audio_bytes)}"
        )
        return reply_text, reply_audio_bytes




    async def send_text_with_tts(
        self,
        content: str,
        session_id: int,
        prompt: Optional[str] = "",
        conversation_history: Optional[list[dict]] = None,
        
        voice: str = "alloy",
        audio_format: str = "mp3",
    ) -> Tuple[str, bytes]:
        """
        Send a text message and get:
            - text response
            - TTS audio bytes of that response
        in a single Responses API call using the TTS-capable model.
        """
        messages = await self._generate_llm_input(
            user_message=content,session_id=session_id,
            prompt=prompt, conversation_history=conversation_history)

        logger.debug(
            f"[session={session_id}] Sending text with TTS via model={self.tts_model}, "
            f"voice={voice}, format={audio_format}, messages={messages}"
        )

        resp = await self.client.responses.create(
            model=self.tts_model,   # "gpt-4o-mini-tts"
            input=messages,
            audio={"voice": voice, "format": audio_format},
        )

        return await self._parse_responses_tts_output(session_id, resp)




