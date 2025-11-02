"""
Enhanced Arabic ASR using Faster-Whisper
Optimized for Quranic recitation
"""

import logging
import tempfile
from typing import Optional

from fastapi import UploadFile
from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)

# Initialize model once (singleton pattern)
_model: Optional[WhisperModel] = None


def get_whisper_model() -> WhisperModel:
    """Lazy load Whisper model (singleton)"""
    global _model
    if _model is None:
        logger.info("Loading Whisper model...")
        # Use 'medium' for better Arabic accuracy, 'small' for faster inference
        _model = WhisperModel(
            "medium",  # Options: tiny, base, small, medium, large-v2, large-v3
            device="cpu",
            compute_type="int8",
            num_workers=2,
            download_root=None  # Uses default cache
        )
        logger.info("Whisper model loaded successfully")
    return _model


async def transcribe_audio(file_path: str) -> str:
    """
    Transcribe Arabic audio file using Faster-Whisper

    Optimizations for Quranic recitation:
    - Language set to Arabic
    - Beam search for better accuracy
    - VAD filter to remove silence
    - Temperature 0 for deterministic output
    """

    try:
        model = get_whisper_model()

        logger.info(f"Transcribing audio: {file_path}")

        # Transcribe with optimized parameters for Arabic Quran
        segments, info = model.transcribe(
            file_path,
            language="ar",  # Force Arabic
            beam_size=5,  # Higher beam size = better accuracy
            best_of=5,  # Generate 5 candidates, pick best
            temperature=0.0,  # Deterministic output
            compression_ratio_threshold=2.4,
            log_prob_threshold=-1.0,
            no_speech_threshold=0.6,
            condition_on_previous_text=True,  # Context from previous segments
            vad_filter=True,  # Voice Activity Detection
            vad_parameters=dict(
                min_silence_duration_ms=500,  # Min silence to split segments
                speech_pad_ms=200  # Padding around speech
            ),
            word_timestamps=False  # Don't need word-level timing
        )

        # Concatenate all segments
        transcript = "".join(seg.text for seg in segments).strip()

        logger.info(f"Transcription complete: {len(transcript)} chars, "
                    f"detected language: {info.language} "
                    f"(probability: {info.language_probability:.2f})")

        return transcript

    except Exception as e:
        logger.exception(f"Transcription failed: {str(e)}")
        raise Exception(f"Audio transcription failed: {str(e)}")


async def transcribe_audio_from_upload(upload_file: UploadFile) -> str:
    """
    Convenience function to transcribe directly from UploadFile
    """

    # Determine suffix
    suffix = ".wav"
    if upload_file.filename.endswith(".m4a"):
        suffix = ".m4a"
    elif upload_file.filename.endswith(".mp3"):
        suffix = ".mp3"
    elif upload_file.filename.endswith(".aac"):
        suffix = ".aac"

    # Save to temp file and transcribe
    with tempfile.NamedTemporaryFile(delete=True, suffix=suffix) as tmp:
        content = await upload_file.read()
        tmp.write(content)
        tmp.flush()

        return await transcribe_audio(tmp.name)
