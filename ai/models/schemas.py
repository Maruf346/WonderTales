"""
models/schemas.py  –  All Pydantic v2 request & response schemas.
"""

from __future__ import annotations
from enum import Enum
from typing import Optional
import re
from pydantic import BaseModel, Field, field_validator


# ──────────────────────────────────────────────────────────────────
#  Enums
# ──────────────────────────────────────────────────────────────────

class Language(str, Enum):
    english = "en"
    french = "fr"
    spanish = "es"
    arabic = "ar"
    hindi = "hi"
    german = "de"
    portuguese = "pt"


class PresetVoice(str, Enum):
    # Primary tier: Main soothing narration (default)
    primary_female = "primary_female"
    primary_male = "primary_male"
    # Secondary tier: Backup & alternative narration
    secondary_female = "secondary_female"
    secondary_male = "secondary_male"
    # Child tier: Character dialogue (use sparingly)
    child_female = "child_female"
    child_male = "child_male"


_LEGACY_PRESET_VOICE_ALIASES = {
    # Legacy backward compatibility
    "storyteller": "primary_female",
    "adult_female": "primary_female",
    "adult_male": "primary_male",
    "teen_female": "secondary_female",
    "teen_male": "secondary_male",
}


class StoryTheme(str, Enum):
    adventure = "adventure"
    fantasy = "fantasy"
    animals = "animals"
    science = "science"
    friendship = "friendship"
    bedtime = "bedtime"
    custom = "custom"


# ──────────────────────────────────────────────────────────────────
#  Child Profile (passed in every story request)
# ──────────────────────────────────────────────────────────────────

class ChildProfile(BaseModel):
    name: str = Field(..., min_length=1, max_length=60, examples=["Amara"])
    age: int = Field(..., ge=2, le=14, examples=[6])
    interests: list[str] = Field(
        default_factory=list,
        max_length=10,
        examples=[["dinosaurs", "space"]],
    )


# ──────────────────────────────────────────────────────────────────
#  Story Generation
# ──────────────────────────────────────────────────────────────────

class StoryGenerateRequest(BaseModel):
    child_profile: ChildProfile
    language: Language = Language.english
    narrator_voice: PresetVoice = Field(
        default=PresetVoice.primary_female,
        examples=[PresetVoice.primary_female.value, PresetVoice.primary_male.value, PresetVoice.secondary_female.value],
        description="Voice for narration. Primary tier recommended for main narration; Secondary/Child for alternatives or dialogue.",
    )
    theme: StoryTheme = StoryTheme.bedtime
    custom_theme: Optional[str] = Field(
        None,
        max_length=200,
        description="Required when theme=custom",
    )
    cloned_voice_id: Optional[str] = Field(
        None,
        description="If set, uses the cloned voice instead of a preset voice.",
    )

    @field_validator("custom_theme")
    @classmethod
    def custom_theme_required(cls, v, info):
        if info.data.get("theme") == StoryTheme.custom and not v:
            raise ValueError("custom_theme is required when theme='custom'")
        return v

    @field_validator("narrator_voice", mode="before")
    @classmethod
    def normalize_narrator_voice(cls, value):
        if isinstance(value, str):
            return _LEGACY_PRESET_VOICE_ALIASES.get(value, value)
        return value

    @field_validator("cloned_voice_id", mode="before")
    @classmethod
    def normalize_cloned_voice_id(cls, value):
        if value in (None, "", "string", "null"):
            return None
        if isinstance(value, str):
            cleaned = value.strip()
            return None if cleaned.lower() in {"string", "null"} else cleaned
        return value


class StoryContinueRequest(BaseModel):
    child_profile: ChildProfile
    story_id: Optional[str] = Field(
        None,
        description="Saved story ID returned by /stories/generate. Preferred for continuation (optimizes token usage).",
    )
    previous_story_text: Optional[str] = Field(
        None,
        min_length=50,
        max_length=8000,
        description="Optional fallback when story_id is not available. Avoid if possible to reduce API token cost.",
    )
    language: Language = Language.english
    narrator_voice: PresetVoice = Field(
        default=PresetVoice.primary_male,
        examples=[PresetVoice.primary_male.value, PresetVoice.secondary_male.value, PresetVoice.child_male.value],
        description="Voice for narration. Primary tier recommended for main narration; Secondary/Child for alternatives or dialogue.",
    )
    cloned_voice_id: Optional[str] = None

    @field_validator("narrator_voice", mode="before")
    @classmethod
    def normalize_narrator_voice(cls, value):
        if isinstance(value, str):
            return _LEGACY_PRESET_VOICE_ALIASES.get(value, value)
        return value

    @field_validator("cloned_voice_id", mode="before")
    @classmethod
    def normalize_cloned_voice_id(cls, value):
        if value in (None, "", "string", "null"):
            return None
        if isinstance(value, str):
            cleaned = value.strip()
            return None if cleaned.lower() in {"string", "null"} else cleaned
        return value

    @field_validator("story_id", mode="before")
    @classmethod
    def normalize_story_id(cls, value):
        if value in (None, "", "string", "null"):
            return None
        if isinstance(value, str):
            cleaned = value.strip()
            return None if cleaned.lower() in {"string", "null"} else cleaned
        return value

    @field_validator("previous_story_text", mode="before")
    @classmethod
    def normalize_previous_story_text(cls, value):
        if value in (None, "", "string", "null"):
            return None
        if isinstance(value, str):
            cleaned = value.strip()
            # normalize and remove whitespace for placeholder detection
            low = re.sub(r"\s+", "", cleaned.lower())
            # treat repeated placeholder tokens like 'stringstringstring' as missing
            if low in {"string", "null"} or re.fullmatch(r"(?:string)+", low):
                return None
            return cleaned
        return value

    @field_validator("previous_story_text")
    @classmethod
    def require_story_reference(cls, value, info):
        if not value and not info.data.get("story_id"):
            raise ValueError("Either story_id or previous_story_text is required")
        return value


# ──────────────────────────────────────────────────────────────────
#  Word-Level Timestamps for TTS Synchronization
# ──────────────────────────────────────────────────────────────────

class WordTimestamp(BaseModel):
    """Word-level timing data for subtitle sync, karaoke, and read-along effects."""
    word: str = Field(..., description="The spoken word text")
    start: float = Field(..., ge=0, description="Start time of word in seconds")
    end: float = Field(..., ge=0, description="End time of word in seconds")


class StoryResponse(BaseModel):
    story_id: str
    story_text: str
    audio_url: str = Field(..., description="Relative URL to download narration audio.")
    language: Language
    voice_used: str
    word_timestamps: Optional[list[WordTimestamp]] = Field(
        None,
        description="Optional word-level timestamps for subtitle sync & read-along effects. May be None if extraction failed (backward compatible)."
    )


# ──────────────────────────────────────────────────────────────────
#  Voice Cloning
# ──────────────────────────────────────────────────────────────────

class VoiceCloneResponse(BaseModel):
    voice_id: str = Field(..., description="ElevenLabs voice ID to use in future requests.")
    voice_name: str
    message: str = "Voice cloned successfully. Use voice_id in story requests."


# ──────────────────────────────────────────────────────────────────
#  Voices list
# ──────────────────────────────────────────────────────────────────

class VoiceInfo(BaseModel):
    slug: str
    voice_id: str
    label: str


class ClonedVoiceInfo(BaseModel):
    voice_id: str
    voice_name: str
    description: Optional[str] = None
    created_at: Optional[str] = None


class VoicesListResponse(BaseModel):
    preset_voices: list[VoiceInfo]
    cloned_voices: list[ClonedVoiceInfo] = Field(default_factory=list)


# ──────────────────────────────────────────────────────────────────
#  Health
# ──────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str = "ok"
    environment: str
