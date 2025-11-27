import aiofiles
import os
import uuid

class AsyncStorage:
    def __init__(self, base_dir: str = "media"):
        self.base_dir = base_dir
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    async def save_file(self, file_data: bytes, ext: str) -> str:
        """Saves bytes to disk asynchronously and returns the path."""
        filename = f"{uuid.uuid4()}.{ext}"
        file_path = os.path.join(self.base_dir, filename)
        
        async with aiofiles.open(file_path, 'wb') as out_file:
            await out_file.write(file_data)
            
        return file_path

    async def file_exists(self, file_path: str) -> bool:
        return os.path.exists(file_path)

storage = AsyncStorage()