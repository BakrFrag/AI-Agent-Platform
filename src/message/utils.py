import magic   
from typing import Iterable
from src.core import logger

ALLOWED_AUDIO_MIME: set[str] = {
    "audio/mpeg",          # .mp3
    "audio/wav",           # .wav
    "audio/x-wav",
    "audio/flac",          # .flac
    "audio/ogg",           # .ogg
    "audio/webm",          # .webm audio
    "audio/aac",           # .aac
}


async def ensure_valid_audio(
    audio_bytes: bytes,
    chunk_size: int = 4096,
) -> bool:
        """
        Validate that the given in-memory bytes look like a supported audio file.
        Raises ValueError if invalid.
        """

        try:
            if not audio_bytes:
                raise ValueError("Empty audio data")
            header = audio_bytes[:chunk_size]
            mime = magic.from_buffer(header, mime=True)
            logger.debug(f"Detected audio MIME type: {mime}")
            if mime not in ALLOWED_AUDIO_MIME:
                raise ValueError(f"Invalid audio MIME type: {mime} and not in allowed types: {ALLOWED_AUDIO_MIME}")
            return True
        except Exception as exc:
            logger.error(f"Error validating audio data: {str(exc)}")
            return False