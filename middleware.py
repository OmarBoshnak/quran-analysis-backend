"""
Custom middleware for logging and monitoring
Add this NEW file to your backend directory
"""

import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all HTTP requests with timing"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Log request
        logger.info(f"→ {request.method} {request.url.path}")

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log response
        logger.info(
            f"← {request.method} {request.url.path} "
            f"[{response.status_code}] {duration:.2f}s"
        )

        # Add timing header
        response.headers["X-Process-Time"] = f"{duration:.4f}"

        return response
