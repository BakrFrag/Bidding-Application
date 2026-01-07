import os
from typing import Optional, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import dj_database_url



class DBSettings(BaseSettings):
    """
    Database settings managed with Pydantic.
    """
    DB_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    DB_HOST: str = "db"
    DB_PORT: int = 5432
    DB_NAME: str = "postgres"

    @property
    def DATABASES(self):
        """
        default database configuration
        """
        url = f"postgres://{self.DB_USER}:{self.POSTGRES_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        
        return {
            "default": dj_database_url.parse(url) 
        }
class AppSettings(DBSettings):
    """
    Application settings managed with Pydantic and env variables handkling.
    """

    # App Metadata
    APP_NAME: str = "Bidding-Application"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Secrets
    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    # REDIS
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

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


APP_SETTINGS = AppSettings()