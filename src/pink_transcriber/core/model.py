"""Model loading and transcription logic using faster-whisper (CPU optimized)."""

from __future__ import annotations

import os
import sys
import logging
from typing import Optional

from pink_transcriber.config import VERBOSE_MODE, get_model_cache_dir

# Enable logging for downloads
if VERBOSE_MODE:
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("faster_whisper").setLevel(logging.DEBUG)
    logging.getLogger("huggingface_hub").setLevel(logging.INFO)

_model: Optional[any] = None


def load_model() -> None:
    """Load Whisper Large-v3-turbo model for CPU."""
    global _model

    model_cache_dir = get_model_cache_dir()
    model_cache_dir.mkdir(exist_ok=True, parents=True)

    os.environ['HF_HOME'] = str(model_cache_dir / "huggingface")
    os.environ['XDG_CACHE_HOME'] = str(model_cache_dir)
    os.environ['HF_HUB_DISABLE_PROGRESS_BARS'] = '0'

    try:
        from faster_whisper import WhisperModel

        if VERBOSE_MODE:
            print("Loading Whisper Large-v3-turbo (CPU, INT8)...", flush=True)

        _model = WhisperModel(
            "deepdml/faster-whisper-large-v3-turbo-ct2",
            device="cpu",
            compute_type="int8",
            download_root=str(model_cache_dir),
        )

        if VERBOSE_MODE:
            print("✓ Model loaded on CPU (INT8)", flush=True)

    except Exception as e:
        print(f"\nERROR: {e}\n", file=sys.stderr)
        sys.exit(1)


def transcribe(audio_path: str) -> str:
    """Transcribe audio file to text."""
    if _model is None:
        raise RuntimeError("Model not loaded")

    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    try:
        segments, info = _model.transcribe(
            audio_path,
            beam_size=5,
            vad_filter=True,
            language=None,
        )

        text_segments = [segment.text for segment in segments]
        result = " ".join(text_segments).strip()

        if VERBOSE_MODE:
            print(f"  Language: {info.language} ({info.language_probability:.2f})", flush=True)

        return result if result else ""

    except Exception as e:
        raise RuntimeError(f"Transcription failed: {e}")


def get_device() -> str:
    """Get current device name."""
    return "CPU (INT8)"


def is_loaded() -> bool:
    """Check if model is loaded and ready."""
    return _model is not None
