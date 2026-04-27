"""
Configuration for the Music Analysis Platform API.
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://music_user:music_password@localhost:5432/music_analysis"
    )
    
    # Redis/Celery
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    celery_broker_url: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    celery_result_backend: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    
    # JWT/Auth
    jwt_secret: str = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]
    
    # Debug
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # YouTube
    youtube_api_key: str = os.getenv("YOUTUBE_API_KEY", "")
    
    # Audio Processing
    essentia_confidence_threshold_bpm: float = 0.7
    essentia_confidence_threshold_key: float = 0.6
    essentia_confidence_threshold_structure: float = 0.5
    
    # Storage
    s3_bucket: str = os.getenv("S3_BUCKET", "music-analysis-platform")
    s3_region: str = os.getenv("S3_REGION", "us-east-1")
    s3_access_key: str = os.getenv("S3_ACCESS_KEY", "")
    s3_secret_key: str = os.getenv("S3_SECRET_KEY", "")
    
    # LLM
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai")
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
