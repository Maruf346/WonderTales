"""
routers/stories.py
───────────────────
POST /stories/generate   – Generate a new story + narration
POST /stories/continue   – Continue an existing story + narration
"""

from pathlib import Path

from fastapi import APIRouter, Request
from models.schemas import (
    StoryGenerateRequest,
    StoryContinueRequest,
    StoryResponse,
)
from services import story_service, narration_service
from services.story_store import load_story_record, save_story_record
from core.exceptions import InvalidInputError

router = APIRouter(prefix="/stories", tags=["Stories"])


@router.post(
    "/generate",
    response_model=StoryResponse,
    summary="Generate a new bedtime story",
    description=(
        "Creates a new AI-generated story tailored to the child's profile, "
        "then narrates it using the selected preset or cloned voice. "
        "Returns story text and an audio file URL."
    ),
)
async def generate_story(body: StoryGenerateRequest, request: Request) -> StoryResponse:
    # 1. Generate story text via OpenAI
    story_text = await story_service.generate_story(
        child=body.child_profile,
        language=body.language,
        theme=body.theme,
        custom_theme=body.custom_theme,
    )

    # 2. Convert text to speech via ElevenLabs
    audio_url, word_timestamps = await narration_service.text_to_speech(
        text=story_text,
        preset_voice_slug=body.narrator_voice.value if not body.cloned_voice_id else None,
        cloned_voice_id=body.cloned_voice_id,
    )

    audio_filename = Path(audio_url).name
    absolute_audio_url = str(request.url_for("audio", path=audio_filename))

    story_record = save_story_record(
        {
            "child_profile": body.child_profile.model_dump(),
            "language": body.language.value,
            "narrator_voice": body.narrator_voice.value,
            "theme": body.theme.value,
            "custom_theme": body.custom_theme,
            "cloned_voice_id": body.cloned_voice_id,
            "story_text": story_text,
            "audio_url": absolute_audio_url,
            "word_timestamps": [ts for ts in word_timestamps] if word_timestamps else None,
            "voice_used": body.cloned_voice_id or body.narrator_voice.value,
        }
    )

    return StoryResponse(
        story_id=story_record["story_id"],
        story_text=story_text,
        audio_url=absolute_audio_url,
        language=body.language,
        voice_used=body.cloned_voice_id or body.narrator_voice.value,
        word_timestamps=word_timestamps,
    )


@router.post(
    "/continue",
    response_model=StoryResponse,
    summary="Continue an existing story",
    description=(
        "Appends a new chapter/segment to a previous story. "
        "Pass the full previous story text as context. "
        "Returns the continuation text and audio."
    ),
)
async def continue_story(body: StoryContinueRequest, request: Request) -> StoryResponse:
    previous_text = body.previous_story_text
    source_story_id = body.story_id

    if source_story_id:
        try:
            source_record = load_story_record(source_story_id)
        except FileNotFoundError as exc:
            raise InvalidInputError(f"Story '{source_story_id}' was not found.") from exc
        previous_text = source_record.get("story_text")
        if not previous_text:
            raise InvalidInputError(f"Story '{source_story_id}' does not contain story_text.")

    # 1. Generate continuation via OpenAI
    continuation_text = await story_service.continue_story(
        child=body.child_profile,
        previous_text=previous_text,
        language=body.language,
    )

    # 2. Narrate continuation
    audio_url, word_timestamps = await narration_service.text_to_speech(
        text=continuation_text,
        preset_voice_slug=body.narrator_voice.value if not body.cloned_voice_id else None,
        cloned_voice_id=body.cloned_voice_id,
    )

    audio_filename = Path(audio_url).name
    absolute_audio_url = str(request.url_for("audio", path=audio_filename))

    combined_story_text = f"{previous_text}\n\n{continuation_text}" if previous_text else continuation_text

    story_record = save_story_record(
        {
            "story_id": source_story_id,
            "parent_story_id": source_story_id,
            "child_profile": body.child_profile.model_dump(),
            "language": body.language.value,
            "narrator_voice": body.narrator_voice.value,
            "cloned_voice_id": body.cloned_voice_id,
            "story_text": combined_story_text,
            "latest_segment_text": continuation_text,
            "audio_url": absolute_audio_url,
            "word_timestamps": [ts for ts in word_timestamps] if word_timestamps else None,
            "voice_used": body.cloned_voice_id or body.narrator_voice.value,
        }
    )

    return StoryResponse(
        story_id=story_record["story_id"],
        story_text=continuation_text,
        audio_url=absolute_audio_url,
        language=body.language,
        voice_used=body.cloned_voice_id or body.narrator_voice.value,
        word_timestamps=word_timestamps,
    )
