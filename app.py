"""
Enhanced FastAPI Backend for Quran Learning App
Production-ready with comprehensive error handling and validation
Version: 2.0.0
"""

import logging
import os
import tempfile
import time
from datetime import datetime
from typing import Optional

from cachetools import TTLCache
from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
    HTTPException,
    BackgroundTasks,
    Query,
    Request,
    Depends
)
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware

from align import tokenize_arabic, wer_and_alignment
from asr import transcribe_audio
from config import settings
from feedback import generate_kid_feedback
from quran_data import validate_surah_ayah, get_max_ayah
from reciters import build_reciter_url
from rules import TajweedAnalyzer, detect_tajweed_hints
from security import verify_api_key, RateLimitConfig

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============ Custom Middleware ============

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all HTTP requests with timing"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Log request
        logger.info(f"→ {request.method} {request.url.path} from {request.client.host}")

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


# ============ Initialize FastAPI App ============

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="LittleBeliever Quran Analysis API",
    description="AI-powered Quran recitation analysis with Tajweed guidance",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add custom middleware
app.add_middleware(RequestLoggingMiddleware)

# CORS Configuration
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1",
    "http://10.0.2.2",  # Android emulator
    "http://localhost:8081",  # React Native Metro
    "http://localhost:19006",  # Expo web
    # Add your production domain here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize cache for expensive operations
tajweed_cache = TTLCache(
    maxsize=settings.CACHE_MAX_SIZE,
    ttl=settings.CACHE_TTL_SECONDS
) if settings.CACHE_ENABLED else None

# Constants from settings
MAX_AUDIO_SIZE = settings.MAX_AUDIO_SIZE
ALLOWED_AUDIO_FORMATS = settings.ALLOWED_AUDIO_FORMATS


# ============ Response Models ============

class AnalysisResponse(BaseModel):
    ok: bool
    wer: float = Field(..., ge=0, le=1, description="Word Error Rate")
    cer: float = Field(..., ge=0, le=1, description="Character Error Rate")
    transcript: str
    summary: str
    rule_hints: list
    alignment_hints: list
    tajweed_analysis: dict
    score: int = Field(..., ge=0, le=100)
    needs_repeat: bool


class RecitationURLResponse(BaseModel):
    ok: bool
    url: str
    reciter_name: str
    surah: int
    ayah: int


class TajweedGuideResponse(BaseModel):
    ok: bool
    text: str
    rules: list
    difficulty_level: str
    estimated_duration: int


class ValidationRequest(BaseModel):
    surah: int
    ayah: int


class ValidationResponse(BaseModel):
    ok: bool
    valid: bool
    message: Optional[str] = None
    max_ayah: Optional[int] = None


class ErrorResponse(BaseModel):
    ok: bool = False
    error: str
    detail: Optional[str] = None


class HealthCheckResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: str
    checks: dict


# ============ Custom Exception Handlers ============

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed messages"""
    logger.error(f"Validation error on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=422,
        content={
            "ok": False,
            "error": "Validation failed",
            "detail": str(exc.errors()),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions consistently"""
    logger.error(f"HTTP exception on {request.url.path}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "ok": False,
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all for unhandled exceptions"""
    logger.exception(f"Unhandled exception on {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "ok": False,
            "error": "Internal server error",
            "detail": "An unexpected error occurred. Please try again.",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# ============ Utility Functions ============

async def cleanup_temp_file(file_path: str):
    """Background task to clean up temporary files"""
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
            logger.info(f"Cleaned up temp file: {file_path}")
    except Exception as e:
        logger.error(f"Failed to clean up {file_path}: {e}")


def validate_audio_file(file: UploadFile) -> None:
    """Validate uploaded audio file"""
    # Check file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_AUDIO_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid audio format. Allowed: {', '.join(ALLOWED_AUDIO_FORMATS)}"
        )

    # Check file size (this is approximate, full size check happens during read)
    if hasattr(file, 'size') and file.size and file.size > MAX_AUDIO_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Audio file too large. Maximum size: {MAX_AUDIO_SIZE / 1024 / 1024}MB"
        )


def validate_arabic_text(text: str) -> None:
    """Validate that text contains Arabic characters"""
    if not text or not text.strip():
        raise HTTPException(
            status_code=400,
            detail="Expected Arabic text cannot be empty"
        )

    # Check if contains at least some Arabic characters
    arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
    if arabic_chars < len(text.strip()) * settings.MIN_ARABIC_RATIO:
        raise HTTPException(
            status_code=400,
            detail=f"Text must contain primarily Arabic characters (at least {int(settings.MIN_ARABIC_RATIO * 100)}%)"
        )


# ============ API Endpoints ============

@app.post("/analyze", response_model=AnalysisResponse)
@limiter.limit(RateLimitConfig.ANALYZE)
async def analyze_recitation(
        request: Request,
        background_tasks: BackgroundTasks,
        audio: UploadFile = File(..., description="Audio file of Quran recitation"),
        expected_arabic: str = Form(..., description="Expected Arabic text"),
        api_key: str = Depends(verify_api_key)
):
    """
    Comprehensive Quran recitation analysis

    **Process:**
    1. ASR (Arabic) → transcript using Whisper
    2. Tokenize & normalize text
    3. Calculate WER + alignment (ref vs hyp)
    4. Detect Tajweed rule violations
    5. Generate child-friendly AI feedback

    **Returns:** Complete analysis with mistakes, Tajweed guidance, and score

    **Rate Limit:** 5 requests per minute
    """

    logger.info(f"Analysis request from {request.client.host} for: {expected_arabic[:50]}...")

    # Validate inputs
    validate_audio_file(audio)
    validate_arabic_text(expected_arabic)

    temp_file_path = None

    try:
        # Save audio to temp file
        suffix = os.path.splitext(audio.filename)[1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            temp_file_path = tmp.name
            content = await audio.read()

            # Check actual file size
            if len(content) > MAX_AUDIO_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"Audio file too large. Maximum size: {MAX_AUDIO_SIZE / 1024 / 1024}MB"
                )

            tmp.write(content)
            tmp.flush()

        logger.info(f"Audio saved to temp file: {temp_file_path}")

        # 1. ASR - Transcribe audio
        transcript = await transcribe_audio(temp_file_path)
        logger.info(f"Transcription: {transcript[:100]}...")

        if not transcript:
            raise HTTPException(
                status_code=400,
                detail="Could not transcribe audio. Please ensure clear recitation."
            )

        # 2. Tokenize (normalize to reduce diacritic noise)
        ref_tokens = tokenize_arabic(expected_arabic)
        hyp_tokens = tokenize_arabic(transcript)

        # 3. WER + alignment
        wer_value, cer_value, alignment_hints = wer_and_alignment(ref_tokens, hyp_tokens)
        logger.info(f"WER: {wer_value:.2f}, CER: {cer_value:.2f}")

        # 4. Tajweed rule hints
        rule_hints = detect_tajweed_hints(expected_arabic, ref_tokens, hyp_tokens)

        # 5. Comprehensive Tajweed analysis
        tajweed_analyzer = TajweedAnalyzer()
        tajweed_analysis = tajweed_analyzer.analyze_full_text(expected_arabic)

        # 6. Generate feedback summary
        summary = await generate_kid_feedback(
            expected_arabic=expected_arabic,
            transcript=transcript,
            wer=wer_value,
            cer=cer_value,
            rule_hints=rule_hints
        )

        # Calculate score (0-100)
        score = max(0, min(100, int((1 - wer_value) * 100)))
        needs_repeat = wer_value > settings.WER_THRESHOLD

        # Schedule cleanup
        background_tasks.add_task(cleanup_temp_file, temp_file_path)

        logger.info(f"Analysis complete. Score: {score}, WER: {wer_value:.2f}")

        return {
            "ok": True,
            "wer": float(wer_value),
            "cer": float(cer_value),
            "transcript": transcript,
            "summary": summary,
            "rule_hints": rule_hints,
            "alignment_hints": alignment_hints,
            "tajweed_analysis": tajweed_analysis,
            "score": score,
            "needs_repeat": needs_repeat
        }

    except HTTPException:
        # Re-raise HTTP exceptions
        if temp_file_path:
            background_tasks.add_task(cleanup_temp_file, temp_file_path)
        raise

    except Exception as e:
        logger.exception(f"Analysis failed: {str(e)}")
        if temp_file_path:
            background_tasks.add_task(cleanup_temp_file, temp_file_path)
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@app.post("/tajweed-guide", response_model=TajweedGuideResponse)
@limiter.limit(RateLimitConfig.GENERAL)
async def get_tajweed_guide(
        request: Request,
        arabic_text: str = Form(..., description="Arabic text for Tajweed analysis"),
        api_key: str = Depends(verify_api_key)
):
    """
    Get comprehensive Tajweed pronunciation guide for Arabic text

    **Returns:** Detailed Tajweed rules, difficulty level, and guidance

    **Rate Limit:** 10 requests per minute

    **Caching:** Results are cached for 1 hour
    """

    validate_arabic_text(arabic_text)

    # Check cache first
    cache_key = hash(arabic_text)
    if tajweed_cache and cache_key in tajweed_cache:
        logger.info("Returning cached Tajweed guide")
        return tajweed_cache[cache_key]

    try:
        analyzer = TajweedAnalyzer()
        guide = analyzer.get_pronunciation_guide(arabic_text)

        result = {
            "ok": True,
            "text": arabic_text,
            "rules": guide['rules'],
            "difficulty_level": guide['difficulty_level'],
            "estimated_duration": guide['estimated_duration']
        }

        # Cache the result
        if tajweed_cache is not None:
            tajweed_cache[cache_key] = result
            logger.info(f"Cached Tajweed guide (cache size: {len(tajweed_cache)})")

        return result

    except Exception as e:
        logger.exception(f"Tajweed guide generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate Tajweed guide: {str(e)}"
        )


@app.get("/recitation", response_model=RecitationURLResponse)
@limiter.limit(RateLimitConfig.GENERAL)
async def get_recitation_url(
        request: Request,
        surah: int = Query(..., ge=1, le=114, description="Surah number (1-114)"),
        ayah: int = Query(..., ge=1, description="Ayah number"),
        reciter_id: int = Query(7, ge=1, description="Reciter ID"),
        api_key: str = Depends(verify_api_key)
):
    """
    Get MP3 URL for a specific Surah and Ayah recitation

    **Reciters:**
    - 1: Abdul Basit
    - 2: Mishary Rashid Alafasy
    - 7: Abu Bakr Al-Shatiri (default)

    **Rate Limit:** 10 requests per minute
    """

    # Validate surah and ayah
    is_valid, error_msg = validate_surah_ayah(surah, ayah)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    try:
        url = build_reciter_url(surah, ayah, reciter_id)

        reciter_names = {
            1: "Abdul Basit",
            2: "Mishary Rashid Alafasy",
            7: "Abu Bakr Al-Shatiri",
            3: "Mahmoud Khalil Al-Hussary",
            4: "Saad Al-Ghamadi"
        }

        return {
            "ok": True,
            "url": url,
            "reciter_name": reciter_names.get(reciter_id, "Unknown Reciter"),
            "surah": surah,
            "ayah": ayah
        }

    except Exception as e:
        logger.exception(f"Failed to build recitation URL: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve recitation URL"
        )


@app.post("/validate-ayah", response_model=ValidationResponse)
@limiter.limit(RateLimitConfig.GENERAL)
async def validate_ayah_endpoint(
        request: Request,
        data: ValidationRequest,
        api_key: str = Depends(verify_api_key)
):
    """
    Validate surah/ayah numbers

    Useful for frontend validation before recording/analysis

    **Rate Limit:** 10 requests per minute
    """
    is_valid, error_msg = validate_surah_ayah(data.surah, data.ayah)
    max_ayah = get_max_ayah(data.surah)

    return {
        "ok": True,
        "valid": is_valid,
        "message": error_msg,
        "max_ayah": max_ayah
    }


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint with dependency status

    Returns service health and status of critical dependencies
    """
    health = {
        "status": "healthy",
        "service": "quran-learning-api",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }

    # Check Whisper model
    try:
        from asr import get_whisper_model
        model = get_whisper_model()
        health["checks"]["whisper"] = {
            "status": "ok",
            "model": settings.WHISPER_MODEL,
            "device": settings.WHISPER_DEVICE
        }
    except Exception as e:
        health["checks"]["whisper"] = {
            "status": "error",
            "error": str(e)
        }
        health["status"] = "degraded"

    # Check Gemini
    if settings.GEMINI_API_KEY:
        health["checks"]["gemini"] = {
            "status": "configured",
            "model": settings.GEMINI_MODEL
        }
    else:
        health["checks"]["gemini"] = {
            "status": "disabled",
            "note": "Using fallback feedback"
        }

    # Check cache
    if tajweed_cache is not None:
        health["checks"]["cache"] = {
            "status": "enabled",
            "items": len(tajweed_cache),
            "max_size": settings.CACHE_MAX_SIZE,
            "ttl": settings.CACHE_TTL_SECONDS
        }
    else:
        health["checks"]["cache"] = {
            "status": "disabled"
        }

    # Check rate limiter
    health["checks"]["rate_limiter"] = {
        "status": "enabled",
        "general_limit": settings.RATE_LIMIT_PER_MINUTE,
        "analyze_limit": settings.RATE_LIMIT_ANALYZE
    }

    return health


@app.get("/")
async def root():
    """API information and links"""
    return {
        "message": "LittleBeliever Quran Learning API",
        "version": "2.0.0",
        "description": "AI-powered Quran recitation analysis with Tajweed guidance",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "analyze": "POST /analyze",
            "tajweed_guide": "POST /tajweed-guide",
            "recitation": "GET /recitation",
            "validate": "POST /validate-ayah"
        },
        "features": [
            "Arabic Speech Recognition (Whisper)",
            "Tajweed Rule Analysis",
            "Child-Friendly AI Feedback",
            "Rate Limiting",
            "Response Caching",
            "Request Logging"
        ]
    }


# ============ Run Server ============

if __name__ == "__main__":
    import uvicorn

    logger.info("=" * 60)
    logger.info("Starting LittleBeliever Quran Learning API")
    logger.info(f"Version: 2.0.0")
    logger.info(f"Log Level: {settings.LOG_LEVEL}")
    logger.info(f"Whisper Model: {settings.WHISPER_MODEL}")
    logger.info(f"Cache Enabled: {settings.CACHE_ENABLED}")
    logger.info(f"API Key Required: {settings.REQUIRE_API_KEY}")
    logger.info("=" * 60)

    uvicorn.run(
        "app:app",  # Changed from just 'app' to "app:app"
        host="0.0.0.0",
        port=8081,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )
