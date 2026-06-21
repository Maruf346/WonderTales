"""
services/narration_service.py
──────────────────────────────
ElevenLabs integration:
  • text_to_speech()    – convert story text → MP3 audio file + word timestamps
  • clone_voice()       – upload recording → create cloned voice model
  • list_preset_voices()– return preset voice catalogue

ElevenLabs API docs: https://elevenlabs.io/docs/api-reference
Voice cloning:       https://elevenlabs.io/docs/api-reference/voice-lab/add-voice
"""

from __future__ import annotations

import base64
import re
import uuid
from pathlib import Path

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from core.config import get_settings
from core.exceptions import NarrationError, VoiceCloningError, VoiceNotFoundError
from core.logging import logger

settings = get_settings()

# Ensure audio storage directory exists at import time
_audio_dir = Path(settings.audio_storage_dir)
_audio_dir.mkdir(parents=True, exist_ok=True)

_HEADERS = {"xi-api-key": settings.elevenlabs_api_key}

# ElevenLabs TTS model – use the calmer multilingual model by default for bedtime narration
_TTS_MODEL = settings.elevenlabs_tts_model


_WORD_PATTERN = re.compile(r"\b[\w]+(?:['-][\w]+)*\b")


# ── Word Timestamp Extraction ──────────────────────────────────────

def _extract_words(text: str) -> list[str]:
    """Extract individual words from text while preserving original casing."""
    return [match.group(0) for match in _WORD_PATTERN.finditer(text)]


def _extract_word_spans(text: str) -> list[tuple[str, int, int]]:
    """Return word tokens together with their character spans in the source text."""
    return [(match.group(0), match.start(), match.end()) for match in _WORD_PATTERN.finditer(text)]


def _alignment_to_word_timestamps(
    text: str,
    characters: list[str],
    character_start_times_seconds: list[float],
    character_end_times_seconds: list[float],
) -> list[dict]:
    """Convert character-level alignment data into word-level timestamps."""
    if not characters or not character_start_times_seconds or not character_end_times_seconds:
        return []
    if len(characters) != len(character_start_times_seconds) or len(characters) != len(character_end_times_seconds):
        return []

    word_timestamps: list[dict] = []

    for word, start_index, end_index in _extract_word_spans(text):
        start_time = None
        end_time = None

        for char_index in range(start_index, min(end_index, len(characters))):
            if characters[char_index].strip():
                if start_time is None:
                    start_time = character_start_times_seconds[char_index]
                end_time = character_end_times_seconds[char_index]

        if start_time is None or end_time is None:
            continue

        start_time = float(start_time)
        end_time = float(end_time)
        if end_time < start_time:
            end_time = start_time

        word_timestamps.append(
            {
                "word": word,
                "start": round(start_time, 2),
                "end": round(end_time, 2),
            }
        )

    return word_timestamps


def _calculate_word_timestamps(
    text: str,
    audio_duration_seconds: float,
) -> list[dict]:
    """Fallback timestamp generator that distributes time monotonically across words."""
    words = _extract_words(text)
    if not words or audio_duration_seconds <= 0:
        return []

    word_spans = _extract_word_spans(text)
    word_weights: list[float] = []

    for word, start_index, end_index in word_spans:
        length_weight = max(1.0, min(2.5, 0.75 + len(word) * 0.12))
        punctuation_weight = 1.0
        trailing_text = text[end_index : min(len(text), end_index + 2)]
        if trailing_text.startswith((".", "!", "?")):
            punctuation_weight = 1.35
        elif trailing_text.startswith((",", ";", ":")):
            punctuation_weight = 1.15
        word_weights.append(length_weight * punctuation_weight)

    total_weight = sum(word_weights)
    if total_weight <= 0:
        return []

    timestamps: list[dict] = []
    current_time = 0.0

    for index, (word, _, _) in enumerate(word_spans):
        remaining_words = len(word_spans) - index
        remaining_time = max(0.0, audio_duration_seconds - current_time)

        if remaining_words == 1:
            word_duration = remaining_time
        else:
            proportional_duration = audio_duration_seconds * (word_weights[index] / total_weight)
            max_allowed = remaining_time - 0.01 * (remaining_words - 1)
            word_duration = max(0.03, min(proportional_duration, max_allowed))

        start_time = current_time
        end_time = min(audio_duration_seconds, start_time + word_duration)

        if end_time < start_time:
            end_time = start_time

        timestamps.append(
            {
                "word": word,
                "start": round(start_time, 2),
                "end": round(end_time, 2),
            }
        )

        current_time = end_time

        if index < len(word_spans) - 1:
            gap = min(0.05, max(0.0, audio_duration_seconds - current_time) / (remaining_words * 4))
            current_time = min(audio_duration_seconds, current_time + gap)

    if timestamps:
        timestamps[-1]["end"] = round(audio_duration_seconds, 2)

    return timestamps


def _get_audio_duration(file_path: Path) -> float:
    """
    Get audio file duration in seconds.
    
    Tries multiple methods:
    1. pydub (requires ffmpeg/libav)
    2. mutagen (pure Python, no external deps)
    3. Fallback: estimate from file size
    """
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_mp3(str(file_path))
        return len(audio) / 1000.0  # Convert milliseconds to seconds
    except ImportError:
        pass
    except Exception as exc:
        logger.debug("pydub.extraction_failed", error=str(exc))
    
    # Fallback: Try mutagen (pure Python, no ffmpeg needed)
    try:
        from mutagen.mp3 import MP3
        audio = MP3(str(file_path))
        if audio.info.length:
            return audio.info.length
    except ImportError:
        pass
    except Exception as exc:
        logger.debug("mutagen.extraction_failed", error=str(exc))
    
    # Fallback: Estimate from file size (rough heuristic)
    # Average MP3 bitrate: ~128 kbps = 16 KB/s
    try:
        file_size_kb = file_path.stat().st_size / 1024
        estimated_duration = (file_size_kb / 16) 
        logger.info(
            "audio_duration.estimated_from_filesize",
            file=file_path.name,
            size_kb=file_size_kb,
            estimated_duration=estimated_duration,
        )
        return estimated_duration
    except Exception as exc:
        logger.warning("audio_duration.all_methods_failed", error=str(exc))
        return None


# ── Helpers ────────────────────────────────────────────────────────

def _resolve_voice_id(
    preset_slug: str | None,
    cloned_voice_id: str | None,
) -> str:
    """Return the ElevenLabs voice ID to use."""
    if cloned_voice_id:
        return cloned_voice_id

    voices = settings.preset_voices
    if preset_slug not in voices:
        raise VoiceNotFoundError(
            f"Voice '{preset_slug}' not found. Available: {list(voices.keys())}"
        )
    return voices[preset_slug]


def _audio_path(filename: str) -> Path:
    return _audio_dir / filename


# ── TTS ────────────────────────────────────────────────────────────

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=8))
async def text_to_speech(
    text: str,
    preset_voice_slug: str | None = None,
    cloned_voice_id: str | None = None,
) -> tuple[str, list[dict] | None]:
    """
    Convert `text` to an MP3 file via ElevenLabs and extract word-level timestamps.
    
    Returns
    -------
    (audio_url, word_timestamps)
        audio_url: relative URL path to the audio file (e.g., "/audio/abc123.mp3")
        word_timestamps: list of {"word", "start", "end"} dicts, or None if extraction failed

    Parameters
    ----------
    text               : Story text to narrate.
    preset_voice_slug  : One of the preset voice slugs (e.g. 'primary_female').
    cloned_voice_id    : ElevenLabs voice ID from a prior clone_voice() call.
    """
    voice_id = _resolve_voice_id(preset_voice_slug, cloned_voice_id)
    base_url = settings.elevenlabs_base_url.rstrip("/")
    url = f"{base_url}/text-to-speech/{voice_id}/with-timestamps"
    fallback_url = f"{base_url}/text-to-speech/{voice_id}"

    payload = {
        "text": text,
        "model_id": _TTS_MODEL,
        "voice_settings": {
            "stability": 0.55,
            "similarity_boost": 0.75,
            "style": 0.30,
            "use_speaker_boost": True,
        },
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, json=payload, headers=_HEADERS)

            if resp.status_code == 404:
                resp = await client.post(fallback_url, json=payload, headers=_HEADERS)
                resp.raise_for_status()

                filename = f"{uuid.uuid4().hex}.mp3"
                file_path = _audio_path(filename)
                file_path.write_bytes(resp.content)

                logger.info("tts.ok", voice_id=voice_id, file=filename, bytes=len(resp.content))

                word_timestamps = None
                audio_duration = _get_audio_duration(file_path)
                if audio_duration is not None:
                    word_timestamps = _calculate_word_timestamps(text, audio_duration)
                    logger.info(
                        "word_timestamps.extracted_fallback",
                        file=filename,
                        word_count=len(word_timestamps),
                        duration=audio_duration,
                    )
                else:
                    logger.warning("word_timestamps.extraction_skipped", file=filename)

                return f"/audio/{filename}", word_timestamps

            resp.raise_for_status()

        response_data = resp.json()
        audio_base64 = response_data.get("audio_base64")
        alignment = response_data.get("alignment") or response_data.get("normalized_alignment")

        if not audio_base64:
            raise NarrationError("ElevenLabs timing response did not include audio_base64.")

        filename = f"{uuid.uuid4().hex}.mp3"
        file_path = _audio_path(filename)
        file_path.write_bytes(base64.b64decode(audio_base64))

        logger.info("tts.ok", voice_id=voice_id, file=filename, bytes=file_path.stat().st_size)

        word_timestamps = None
        if alignment:
            word_timestamps = _alignment_to_word_timestamps(
                text=text,
                characters=alignment.get("characters", []),
                character_start_times_seconds=alignment.get("character_start_times_seconds", []),
                character_end_times_seconds=alignment.get("character_end_times_seconds", []),
            )
            logger.info(
                "word_timestamps.extracted",
                file=filename,
                word_count=len(word_timestamps),
                duration=word_timestamps[-1]["end"] if word_timestamps else None,
            )

        if not word_timestamps:
            audio_duration = _get_audio_duration(file_path)
            if audio_duration is not None:
                word_timestamps = _calculate_word_timestamps(text, audio_duration)
                logger.warning(
                    "word_timestamps.fallback_estimation_used",
                    file=filename,
                    word_count=len(word_timestamps),
                    duration=audio_duration,
                )

        return f"/audio/{filename}", word_timestamps

    except httpx.HTTPStatusError as exc:
        body = exc.response.text
        logger.error("tts.failed", status=exc.response.status_code, body=body)
        raise NarrationError(f"ElevenLabs TTS error {exc.response.status_code}: {body}") from exc
    except Exception as exc:
        logger.error("tts.error", error=str(exc))
        raise NarrationError(str(exc)) from exc


# ── Voice Cloning ──────────────────────────────────────────────────

async def clone_voice(
    voice_name: str,
    audio_bytes: bytes,
    audio_content_type: str = "audio/mpeg",
    description: str = "Family voice for WonderTels",
) -> tuple[str, str]:
    """
    Clone a voice using ElevenLabs Instant Voice Cloning API.

    Parameters
    ----------
    voice_name         : Label for the cloned voice (e.g. "Mum's Voice" or "Dad's Voice").
    audio_bytes        : Raw audio file bytes (MP3/WAV/M4A, up to 5 min).
    audio_content_type : MIME type of the upload.
    description        : Short description stored in ElevenLabs.

    Returns
    -------
    (voice_id, voice_name)  – store voice_id in your database.

    ElevenLabs docs
    ---------------
    POST /v1/voices/add
    multipart/form-data fields:
      name        – string
      description – string
      files       – audio file(s)
    """
    url = f"{settings.elevenlabs_base_url}/voices/add"

    # Determine a sensible file extension from content type
    ext_map = {
        "audio/mpeg": "mp3",
        "audio/mp3": "mp3",
        "audio/wav": "wav",
        "audio/x-wav": "wav",
        "audio/m4a": "m4a",
        "audio/x-m4a": "m4a",
        "audio/mp4": "m4a",
        "audio/webm": "webm",
    }
    ext = ext_map.get(audio_content_type, "mp3")

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                url,
                headers=_HEADERS,
                data={"name": voice_name, "description": description},
                files={"files": (f"voice_sample.{ext}", audio_bytes, audio_content_type)},
            )
            resp.raise_for_status()

        data = resp.json()
        voice_id: str = data["voice_id"]
        logger.info("voice_clone.ok", voice_id=voice_id, name=voice_name)
        return voice_id, voice_name

    except httpx.HTTPStatusError as exc:
        body = exc.response.text
        logger.error("voice_clone.failed", status=exc.response.status_code, body=body)
        raise VoiceCloningError(
            f"ElevenLabs cloning error {exc.response.status_code}: {body}"
        ) from exc
    except Exception as exc:
        logger.error("voice_clone.error", error=str(exc))
        raise VoiceCloningError(str(exc)) from exc


# ── Preset voice catalogue ─────────────────────────────────────────

def get_preset_voices() -> list[dict]:
    """Return preset voice catalog organized by tier for bedtime stories."""
    labels = {
        # Primary tier: Optimized for calm, soothing main narration
        "primary_female": "Primary Female – Charlotte (soft, nurturing, most soothing)",
        "primary_male": "Primary Male – Daniel (warm, reassuring, most soothing)",
        # Secondary tier: Optimized for softer alternative narration
        "secondary_female": "Secondary Female – Rachel (clear, gentle alternative)",
        "secondary_male": "Secondary Male – Liam (calm, alternative storyteller)",
        # Child tier: For character dialogue only (use sparingly)
        "child_female": "Child Female – Matilda (playful, for dialogue)",
        "child_male": "Child Male – George (bright, for dialogue)",
    }
    return [
        {"slug": slug, "voice_id": vid, "label": labels.get(slug, slug)}
        for slug, vid in settings.preset_voices.items()
    ]
