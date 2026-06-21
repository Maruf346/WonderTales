"""
routers/voices.py
──────────────────
GET  /voices              – List all preset voices
POST /voices/clone        – Clone a family voice (Premium, experimental)
"""

from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from models.schemas import VoiceCloneResponse, VoicesListResponse, VoiceInfo, ClonedVoiceInfo
from services.narration_service import clone_voice, get_preset_voices
from services.voice_store import save_cloned_voice, list_cloned_voices
from core.config import get_settings
from core.logging import logger

router = APIRouter(prefix="/voices", tags=["Voices"])
settings = get_settings()

_ALLOWED_AUDIO_TYPES = {
    "audio/mpeg",
    "audio/mp3",
    "audio/wav",
    "audio/x-wav",
    "audio/m4a",
    "audio/x-m4a",
    "audio/mp4",
    "audio/webm",
}

# 5 minutes × 64 kbps MP3 ≈ 2.4 MB. Allow up to 30 MB to be safe with WAV.
_MAX_FILE_SIZE_BYTES = 30 * 1024 * 1024


@router.get(
    "",
    response_model=VoicesListResponse,
    summary="List available preset voices",
    description="Returns all preconfigured narrator voices available for story narration.",
)
async def list_voices() -> VoicesListResponse:
    preset = [VoiceInfo(**v) for v in get_preset_voices()]
    cloned = [ClonedVoiceInfo(**r) for r in list_cloned_voices()]
    return VoicesListResponse(preset_voices=preset, cloned_voices=cloned)


@router.post(
    "/clone",
    response_model=VoiceCloneResponse,
    summary="Clone a family voice  [Premium / Experimental]",
    description=(
        "Upload a voice recording (MP3, WAV, M4A – up to 5 minutes) "
        "to create a personalised narrator voice via ElevenLabs Instant Voice Cloning. "
        "The returned `voice_id` can be passed as `cloned_voice_id` in story requests. "
        "\n\n⚠️ **Experimental feature** – availability depends on your ElevenLabs plan."
    ),
)
async def clone_family_voice(
    voice_name: str = Form(
        ...,
        description="Friendly name for this voice (e.g. 'Mum's Bedtime Voice')",
        max_length=80,
    ),
    description: str = Form(
        default="Family narrator voice for WonderTels",
        max_length=500,
    ),
    audio_file: UploadFile = File(
        ...,
        description="Audio recording – MP3 / WAV / M4A, max 5 minutes.",
    ),
) -> VoiceCloneResponse:
    # Validate MIME type
    raw_content_type = audio_file.content_type or ""
    content_type = raw_content_type.split(";", 1)[0].strip().lower()
    if content_type not in _ALLOWED_AUDIO_TYPES:
        raise HTTPException(
            status_code=415,
            detail=(
                f"Unsupported audio format '{raw_content_type}'. "
                f"Allowed: {sorted(_ALLOWED_AUDIO_TYPES)}"
            ),
        )

    # Read and size-check
    audio_bytes = await audio_file.read()
    if len(audio_bytes) > _MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({len(audio_bytes) // 1024} KB). Maximum is 30 MB.",
        )
    if len(audio_bytes) < 1024:
        raise HTTPException(
            status_code=400,
            detail="Audio file is too short. Please provide at least a few seconds of clean speech.",
        )

    logger.info(
        "voice_clone.request",
        voice_name=voice_name,
        content_type=content_type,
        size_kb=len(audio_bytes) // 1024,
    )

    voice_id, name = await clone_voice(
        voice_name=voice_name,
        audio_bytes=audio_bytes,
        audio_content_type=content_type,
        description=description,
    )

    # persist cloned voice metadata for later retrieval
    try:
        save_cloned_voice(voice_id=voice_id, voice_name=name, description=description)
    except Exception as exc:
        logger.warning("voice_store.save_failed", voice_id=voice_id, error=str(exc))

    return VoiceCloneResponse(voice_id=voice_id, voice_name=name)


@router.get(
    "/cloned",
    summary="List cloned voices",
    description="Returns previously cloned voice models created via /voices/clone.",
)
async def list_clones():
    records = list_cloned_voices()
    return {"cloned_voices": records}
