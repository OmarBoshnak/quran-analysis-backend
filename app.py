"""
Enhanced FastAPI Backend for Quran Learning App
Production-ready with comprehensive error handling and validation
"""

import logging
import os
import tempfile
from typing import Optional

from align import tokenize_arabic, wer_and_alignment
from asr import transcribe_audio
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from feedback import generate_kid_feedback
from pydantic import BaseModel, Field
from reciters import build_reciter_url
from rules import TajweedAnalyzer, detect_tajweed_hints

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LittleBeliever Quran Analysis API",
    description="AI-powered Quran recitation analysis with Tajweed guidance",
    version="2.0.0"
)

# CORS Configuration
origins = [
    "http://localhost",
    "http://127.0.0.1",
    "http://10.0.2.2",  # Android emulator
    "http://localhost:8081",  # React Native Metro
    # Add your production domain here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants
MAX_AUDIO_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_AUDIO_FORMATS = [".m4a", ".wav", ".mp3", ".aac"]


# Response Models
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


class ErrorResponse(BaseModel):
    ok: bool = False
    error: str
    detail: Optional[str] = None


# Custom Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    """Handle validation errors with detailed messages"""
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={
            "ok": False,
            "error": "Validation failed",
            "detail": str(exc.errors())
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Handle HTTP exceptions consistently"""
    logger.error(f"HTTP exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "ok": False,
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Catch-all for unhandled exceptions"""
    logger.exception(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "ok": False,
            "error": "Internal server error",
            "detail": "An unexpected error occurred. Please try again."
        }
    )


# Utility Functions
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
        raise HTTPException(status_code=400, detail="Expected Arabic text cannot be empty")

    # Check if contains at least some Arabic characters
    arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
    if arabic_chars < len(text.strip()) * 0.3:  # At least 30% Arabic
        raise HTTPException(
            status_code=400,
            detail="Text must contain primarily Arabic characters"
        )


# API Endpoints
@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_recitation(
        background_tasks: BackgroundTasks,
        audio: UploadFile = File(..., description="Audio file of Quran recitation"),
        expected_arabic: str = Form(..., description="Expected Arabic text")
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
    """

    logger.info(f"Analysis request received for: {expected_arabic[:50]}...")

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
        needs_repeat = wer_value > 0.20  # >20% error rate

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
async def get_tajweed_guide(
        arabic_text: str = Form(..., description="Arabic text for Tajweed analysis")
):
    """
    Get comprehensive Tajweed pronunciation guide for Arabic text

    **Returns:** Detailed Tajweed rules, difficulty level, and guidance
    """

    validate_arabic_text(arabic_text)

    try:
        analyzer = TajweedAnalyzer()
        guide = analyzer.get_pronunciation_guide(arabic_text)

        return {
            "ok": True,
            "text": arabic_text,
            "rules": guide['rules'],
            "difficulty_level": guide['difficulty_level'],
            "estimated_duration": guide['estimated_duration']
        }

    except Exception as e:
        logger.exception(f"Tajweed guide generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate Tajweed guide: {str(e)}"
        )


@app.get("/recitation", response_model=RecitationURLResponse)
async def get_recitation_url(
        surah: int = Field(..., ge=1, le=114, description="Surah number (1-114)"),
        ayah: int = Field(..., ge=1, description="Ayah number"),
        reciter_id: int = Field(7, ge=1, description="Reciter ID")
):
    """
    Get MP3 URL for a specific Surah and Ayah recitation

    **Reciters:**
    - 1: Abdul Basit
    - 2: Mishary Rashid Alafasy
    - 7: Abu Bakr Al-Shatiri (default)
    """

    try:
        url = build_reciter_url(surah, ayah, reciter_id)

        reciter_names = {
            1: "Abdul Basit",
            2: "Mishary Rashid Alafasy",
            7: "Abu Bakr Al-Shatiri"
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


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "quran-learning-api",
        "version": "2.0.0"
    }


@app.get("/")
async def root():
    """API information"""
    return {
        "message": "Quran Learning API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8081,
        reload=True,
        log_level="info"
    )
