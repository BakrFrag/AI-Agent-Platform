from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application-wide configuration settings.
    """
    APP_VERSION: str  
    ENV: str = "Development" 
    DATABASE_URL: str  
    OPENAI_API_KEY: str
    LOG_LEVEL: str = "DEBUG" if ENV == "Development" else "INFO" # logging level as per environment
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent.parent / '.env'),extra='ignore')
    CELERY_BROKER_URL: str  
    CELERY_RESULT_BACKEND: str  

settings = Settings()
