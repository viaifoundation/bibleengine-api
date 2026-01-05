"""Configuration settings for the BibleEngine API."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    environment: str = "development"
    database_url: str
    secret_key: str
    wiki_base_url: str = "https://bible.world"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

