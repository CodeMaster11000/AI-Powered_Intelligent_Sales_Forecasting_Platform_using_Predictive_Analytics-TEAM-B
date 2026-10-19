import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "SalesGenie AI Platform"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    
    # AI / LLM Configuration (Jayant's AI Engine)
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")
    DEFAULT_LLM_PROVIDER: str = "gemini"  # "gemini" or "openai" or "rule_based_fallback"
    
    # Database Configuration (PostgreSQL with SQLite fallback for offline development)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./salesgenie.db"
    )
    
    # Platform Settings
    CORS_ORIGINS: list = ["*"]
    
    model_config = {"env_file": ".env", "extra": "allow"}

settings = Settings()
