"""
Enhanced Arabic ASR using Faster-Whisper
Optimized for Quranic recitation with async support
Version: 2.0.0
"""

import asyncio
import logging
import tempfile
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from fastapi import UploadFile
from faster_whisper import WhisperModel

from config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Initialize model once (singleton pattern)
_model: Optional[WhisperModel] = None

# Thread pool for async execution
_executor = ThreadPoolExecutor(max_workers=settings.WHISPER_NUM_WORKERS)


def get_whisper_model() -> WhisperModel:
    """
    Lazy load Whisper model (singleton pattern)

    Model is loaded once and reused for all transcription requests
    to avoid expensive reloading on each request.

    Returns:
        WhisperModel: Initialized Faster-Whisper model
    """
    global _model
    if _model is None:
        logger.info(f"Loading Whisper model: {settings.WHISPER_MODEL}...")
        logger.info(f"Device: {settings.WHISPER_DEVICE}, Compute type: {settings.WHISPER_COMPUTE_TYPE}")

        try:
            _model = WhisperModel(
                settings.WHISPER_MODEL,  # Model size from settings
                device=settings.WHISPER_DEVICE,  # CPU or CUDA
                compute_type=settings.WHISPER_COMPUTE_TYPE,  # int8, int16, float16, float32
                num_workers=settings.WHISPER_NUM_WORKERS,  # Number of CPU threads
                download_root=None  # Uses default cache directory
            )
            logger.info("✓ Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"✗ Failed to load Whisper model: {str(e)}")
            raise RuntimeError(f"Could not initialize Whisper model: {str(e)}")

    return _model


def _transcribe_sync(file_path: str) -> str:
    """
    Synchronous transcription function (runs in thread pool)

    This function performs the actual transcription using Faster-Whisper.
    It's designed to run in a separate thread to avoid blocking the event loop.

    Parameters:
        file_path: Path to the audio file to transcribe

    Returns:
        str: Transcribed Arabic text

    Raises:
        Exception: If transcription fails
    """
    try:
        model = get_whisper_model()
        logger.info(f"Starting transcription for: {file_path}")

        # Transcribe with optimized parameters for Arabic Quran recitation
        segments, info = model.transcribe(
            file_path,
            language="ar",  # Force Arabic language
            beam_size=5,  # Higher beam size = better accuracy (but slower)
            best_of=5,  # Generate 5 candidates, pick best
            temperature=0.0,  # Deterministic output (no randomness)
            compression_ratio_threshold=2.4,  # Reject low-quality audio
            log_prob_threshold=-1.0,  # Threshold for token acceptance
            no_speech_threshold=0.6,  # Threshold to detect silence
            condition_on_previous_text=True,  # Use context from previous segments
            vad_filter=True,  # Voice Activity Detection to remove silence
            vad_parameters=dict(
                min_silence_duration_ms=500,  # Min silence to split segments
                speech_pad_ms=200  # Padding around detected speech
            ),
            word_timestamps=False  # Don't need word-level timing (faster)
        )

        # Concatenate all segments into final transcript
        transcript = "".join(seg.text for seg in segments).strip()

        # Log transcription results
        logger.info(
            f"✓ Transcription complete: {len(transcript)} characters, "
            f"Language: {info.language} "
            f"(confidence: {info.language_probability:.2%})"
        )

        # Warn if language detection confidence is low
        if info.language != "ar":
            logger.warning(
                f"⚠ Expected Arabic but detected: {info.language} "
                f"(confidence: {info.language_probability:.2%})"
            )

        if info.language_probability < 0.7:
            logger.warning(
                f"⚠ Low language detection confidence: {info.language_probability:.2%}"
            )

        return transcript

    except Exception as e:
        logger.exception(f"✗ Transcription failed for {file_path}: {str(e)}")
        raise Exception(f"Audio transcription failed: {str(e)}")


async def transcribe_audio(file_path: str) -> str:
    """
    Transcribe Arabic audio file using Faster-Whisper (async wrapper)

    This function wraps the synchronous transcription in an async executor
    to prevent blocking the FastAPI event loop during the (potentially long)
    transcription process.

    Optimizations for Quranic recitation:
    - Language set to Arabic
    - Beam search for better accuracy
    - VAD filter to remove silence
    - Temperature 0 for deterministic output

    Parameters:
        file_path: Path to the audio file to transcribe

    Returns:
        str: Transcribed Arabic text

    Raises:
        Exception: If transcription fails

    Example:
    >>> transcript = await transcribe_audio("/tmp/recitation.m4a")
    >>> print(transcript)
        'بسم الله الرحمن الرحيم'
    """
    loop = asyncio.get_event_loop()

    # Run synchronous transcription in thread pool
    try:
        transcript = await loop.run_in_executor(
            _executor,
            _transcribe_sync,
            file_path
        )
        return transcript
    except Exception as e:
        logger.error(f"Async transcription wrapper failed: {str(e)}")
        raise


async def transcribe_audio_from_upload(upload_file: UploadFile) -> str:
    """
    Convenience function to transcribe directly from FastAPI UploadFile

    This function handles the entire pipeline:
    1. Reads the uploaded file
    2. Saves it to a temporary file
    3. Transcribes the audio
    4. Cleans up the temporary file

    Parameters:
        upload_file: FastAPI UploadFile object

    Returns:
        str: Transcribed Arabic text

    Raises:
        Exception: If transcription fails

    Example:
        >>> @app.post("/transcribe")
        >>> async def transcribe_endpoint(audio: UploadFile = File(...)):
        >>>     transcript = await transcribe_audio_from_upload(audio)
        >>>     return {"transcript": transcript}
    """

    # Determine file suffix from filename
    suffix = ".wav"  # Default
    filename = upload_file.filename or ""

    if filename.endswith(".m4a"):
        suffix = ".m4a"
    elif filename.endswith(".mp3"):
        suffix = ".mp3"
    elif filename.endswith(".aac"):
        suffix = ".aac"
    elif filename.endswith(".wav"):
        suffix = ".wav"
    elif filename.endswith(".ogg"):
        suffix = ".ogg"
    elif filename.endswith(".flac"):
        suffix = ".flac"

    logger.info(f"Processing upload: {filename} (format: {suffix})")

    # Save to temp file and transcribe
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            temp_file_path = tmp.name

            # Read and write file content
            content = await upload_file.read()
            tmp.write(content)
            tmp.flush()

            logger.info(f"Saved upload to temp file: {temp_file_path} ({len(content)} bytes)")

        # Transcribe the audio
        transcript = await transcribe_audio(temp_file_path)

        return transcript

    finally:
        # Clean up temp file
        if temp_file_path:
            try:
                import os
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    logger.info(f"Cleaned up temp file: {temp_file_path}")
            except Exception as e:
                logger.error(f"Failed to clean up temp file {temp_file_path}: {e}")


def get_model_info() -> dict:
    """
    Get information about the loaded Whisper model

    Returns:
        dict: Model configuration and status
    """
    return {
        "model_loaded": _model is not None,
        "model_name": settings.WHISPER_MODEL,
        "device": settings.WHISPER_DEVICE,
        "compute_type": settings.WHISPER_COMPUTE_TYPE,
        "num_workers": settings.WHISPER_NUM_WORKERS,
    }


def unload_model():
    """
    Unload the Whisper model from memory

    Useful for cleanup or testing purposes
    """
    global _model
    if _model is not None:
        logger.info("Unloading Whisper model from memory")
        del _model
        _model = None


def shutdown_executor():
    """
    Shutdown the thread pool executor

    Should be called during application shutdown
    """
    global _executor
    if _executor is not None:
        logger.info("Shutting down transcription thread pool")
        _executor.shutdown(wait=True)
        _executor = None
