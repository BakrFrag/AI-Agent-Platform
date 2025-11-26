from __future__ import annotations
from pathlib import Path
from typing import Protocol, Optional, runtime_checkable, Any


@runtime_checkable
class LLMClientInterface(Protocol):
    """
    Interface / contract for chat + voice OpenAI client.
    Useful for dependency injection and unit testing.
    """

    async def send_text_message(
        self,
        content: str,
        *,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[list[dict[str, Any]]] = None,
    ) -> str:
        raise NotImplementedError("Method should be implemented by subclass")

    async def text_to_speech(
        self,
        text: str,
        output_path: str | Path,
        *,
        voice: str = "alloy",
        format: str = "wav",
    ) -> Path:
        raise NotImplementedError("Method should be implemented by subclass")

    async def speech_to_text(
        self,
        audio_path: str | Path,
        *,
        prompt: Optional[str] = None,
        language: Optional[str] = None,
    ) -> str:
        raise NotImplementedError("Method should be implemented by subclass")