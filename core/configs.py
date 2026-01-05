import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
import dj_database_url

class AppSettings(BaseSettings):
    """
    Application settings managed with Pydantic and env variables handkling.
    """

    # App Metadata
    APP_NAME: str = "Bidding-Application"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Secrets
    SECRET_KEY: str
    DATABASE_URL: Optional[str] = None
    REDIS_URL: str = "redis://127.0.0.1:6379/0"
    
    # Logging
    LOG_LEVEL: str = "DEBUG"
    
    @property
    def DATABASES(self):

        return {
            "default":  dj_database_url.parse(self.DATABASE_URL) if self.DATABASE_URL else dj_database_url.config(
        default=f"postgres://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )}

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


APP_SETTINGS = AppSettings()