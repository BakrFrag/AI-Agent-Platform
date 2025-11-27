import aiofiles
import magic   # pip install python-magic
from typing import Iterable


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
    file_path: str,
    allowed_mime: Iterable[str] = ALLOWED_AUDIO_MIME,
    chunk_size: int = 2048,
) -> bool:
    """
    Validate that a file is a correct audio type.

    Checks:
    1. File exists & accessible
    2. MIME type using libmagic
    3. Content-based signature detection
    """
    # Read a small chunk asynchronously
    try:
        async with aiofiles.open(file_path, "rb") as f:
            header = await f.read(chunk_size)
    except Exception as e:
        raise ValueError(f"File cannot be opened: {e}")
    mime = magic.from_buffer(header, mime=True)
    if mime not in allowed_mime:
        raise ValueError(f"Invalid audio type: detected '{mime}'")
    return True
