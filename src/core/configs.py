from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application-wide configuration settings.
    """
    APP_VERSION: str  # application version
    ENV: str = "Development" # env can be Development, Production, or Testing
    DATABASE_URL: str  # database connection URL default to local sqlite db
    OPENAI_API_KEY: str # open api key for accessing OpenAI services
    LOG_LEVEL: str = "DEBUG" if ENV == "Development" else "INFO" # logging level as per environment
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent.parent / '.env'),
        extra='ignore'
    )
   

settings = Settings()
