import os
from typing import Optional, Union
from pydantic import Field, field_validator
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

    #Allowed Hosts 
    ALLOWED_HOSTS: Union[str, list[str]] = Field(default=["localhost", "127.0.0.1"])

    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def parse_allowed_hosts(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v


    @property
    def DATABASES(self):

        return {
            "default":  dj_database_url.parse(self.DATABASE_URL) if self.DATABASE_URL else dj_database_url.config(
        default=f"postgres://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )}

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


APP_SETTINGS = AppSettings()