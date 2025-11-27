import os
from pathlib import Path
from typing import Optional
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
        logger.debug(f"Sending message to OpenAI: {content} within session {session_id} and system prompt: {prompt} including {len(conversation_history) if conversation_history else 0} previous messages")

        messages: list[dict] = []
        messages.append({"role": "system", "content": prompt} )  if prompt else None
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": content})
        response = await self.client.responses.create(
            model=self.text_model,
            input = content
        )
        logger.debug(f"Received response from OpenAI for message {content} within session {session_id}: {response}")
        return response.output_text 

    
    async def text_to_speech(
        self,
        text: str,
        output_path: str | Path,
        *,
        voice: str = "alloy",   # pick a default from docs :contentReference[oaicite:3]{index=3}
        format: str = "wav",    # e.g. "wav", "mp3"
    ) -> Path:
        """
        Convert text to speech and save to `output_path`.

        :param text: text to synthesize
        :param output_path: where to save the audio file
        :param voice: voice name (depends on the model)
        :param format: output audio format (e.g. 'mp3', 'wav')
        :return: Path to saved audio file
        """

        output_path = Path(output_path)

        # Audio TTS endpoint :contentReference[oaicite:4]{index=4}
        result = await self.client.audio.speech.create(
            model=self.tts_model,
            voice=voice,
            input=text,
            format=format,
        )

        # `result` is bytes-like audio content for TTS
        output_path.write_bytes(result)
        return output_path

    
    async def speech_to_text(
        self,
        audio_path: str | Path,
        *,
        prompt: Optional[str] = None,
        language: Optional[str] = None,
    ) -> str:
        """
        Transcribe speech from a local audio file to text.

        :param audio_path: path to an audio file (wav, mp3, m4a, etc.)
        :param prompt: optional transcription hint
        :param language: optional language hint (e.g. 'en', 'ar')
        :return: transcript text
        """

        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        with audio_path.open("rb") as f:
            transcription = await self.client.audio.transcriptions.create(
                model=self.stt_model,
                file=f,
                prompt=prompt,
                language=language,
            )

        # The field name can vary by model; usually `text`
        return getattr(transcription, "text", "")



