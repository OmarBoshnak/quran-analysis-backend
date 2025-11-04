"""
Centralized configuration management
"""

from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Security
    API_KEY: str = "dev-key-change-in-production"
    REQUIRE_API_KEY: bool = False

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: str = "10/minute"
    RATE_LIMIT_ANALYZE: str = "5/minute"

    # Audio Processing
    MAX_AUDIO_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_AUDIO_FORMATS: List[str] = [".m4a", ".wav", ".mp3", ".aac"]

    # ASR (Whisper)
    WHISPER_MODEL: str = "medium"
    WHISPER_DEVICE: str = "cpu"
    WHISPER_COMPUTE_TYPE: str = "int8"
    WHISPER_NUM_WORKERS: int = 2

    # Gemini AI
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # Analysis Thresholds
    WER_THRESHOLD: float = 0.20
    MIN_ARABIC_RATIO: float = 0.3
    PASSING_SCORE: int = 80

    # Caching
    CACHE_ENABLED: bool = True
    CACHE_TTL_SECONDS: int = 3600
    CACHE_MAX_SIZE: int = 100

    # Monitoring
    ENABLE_METRICS: bool = True
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = "sqlite:///./quran.db"

    # JWT Authentication
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ACCESS_TOKEN_EXPIRES: int = 3600  # 1 hour
    JWT_REFRESH_TOKEN_EXPIRES: int = 604800  # 7 days

    # API Settings
    API_VERSION: str = "v1"
    API_PREFIX: str = "/api"

    # Audio CDN
    AUDIO_CDN_BASE_URL: str = "https://cdn.islamic.network/quran/audio"

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Don't validate if env file doesn't exist
        env_file_missing_ok = True


# Singleton instance
settings = Settings()
