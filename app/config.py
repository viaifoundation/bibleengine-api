"""Configuration settings for the BibleEngine API."""
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    environment: str = "development"  # development or production
    database_url: str
    secret_key: str
    wiki_base_url: str = "https://bible.world"
    
    # CORS settings
    cors_origins: str = "*"  # Comma-separated list of allowed origins
    
    # API settings
    api_title: str = "BibleEngine API"
    api_version: str = "1.0.0"
    
    # Logging
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"
    
    @property
    def allowed_origins(self) -> List[str]:
        """Get list of allowed CORS origins."""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

