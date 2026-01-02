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
    DATABASE_URL: str = "sqlite:///db.sqlite3"
    REDIS_URL: str = "redis://127.0.0.1:6379/0"
    
    # Logging
    LOG_LEVEL: str = "DEBUG"
    
    @property
    def DATABASES(self):
        """
        Helper to convert DATABASE_URL to Django's DICT format
        """
        return {"default": dj_database_url.parse(self.DATABASE_URL)}

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


app_settings = AppSettings()