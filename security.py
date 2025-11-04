"""
Authentication and security utilities
Add this NEW file to your backend directory
"""

import logging

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

from config import settings

logger = logging.getLogger(__name__)

# API Key header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Verify API key from request header

    Usage in endpoints:
        async def my_endpoint(api_key: str = Depends(verify_api_key)):
            ...
    """
    # Skip validation in development if not required
    if not settings.REQUIRE_API_KEY:
        return "dev-mode"

    if not api_key:
        logger.warning("API request without key")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key required. Add X-API-Key header."
        )

    if api_key != settings.API_KEY:
        logger.warning(f"Invalid API key attempt: {api_key[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )

    return api_key


class RateLimitConfig:
    """Rate limiting configuration"""
    GENERAL = settings.RATE_LIMIT_PER_MINUTE
    ANALYZE = settings.RATE_LIMIT_ANALYZE
    TRANSCRIBE = "3/minute"
