"""
Configuration management for the application.
Loads environment variables and provides settings.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    SERPER_API_KEY: str
    FIRECRAWL_API_KEY: str
    AZURE_OPENAI_API_KEY: str | None = None
    
    # Database
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "product_sentiment"
    
    # Server
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # API Settings
    SERPER_BASE_URL: str = "https://google.serper.dev/search"
    FIRECRAWL_BASE_URL: str = "https://api.firecrawl.dev/v2/scrape"
    
    # Azure OpenAI Settings
    AZURE_OPENAI_ENDPOINT: str | None = None
    AZURE_OPENAI_DEPLOYMENT: str | None = None
    AZURE_OPENAI_API_VERSION: str = "2024-02-15-preview"
    AZURE_OPENAI_MODEL: Optional[str] = None

    # Google Gemini Settings
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: Optional[str] = "gemini-2.5-flash"
    
    # Processing Settings
    MAX_CONCURRENT_SCRAPERS: int = 4
    SCRAPER_TIMEOUT: int = 30000  # milliseconds
    SERPER_RESULTS_COUNT: int = 50
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields in .env file


# Global settings instance
settings = Settings()

