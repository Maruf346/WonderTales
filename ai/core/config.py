"""
core/config.py  –  Centralised settings via pydantic-settings.
All values come from environment variables / .env file.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── OpenAI ────────────────────────────────────────────────
    openai_api_key: str
    openai_model: str = "gpt-4o"
    openai_max_tokens: int = 1500
    openai_temperature: float = 0.85
    openai_presence_penalty: float = 0.6
    openai_frequency_penalty: float = 0.4

    # ── ElevenLabs ────────────────────────────────────────────
    elevenlabs_api_key: str
    elevenlabs_base_url: str = "https://api.elevenlabs.io/v1"
    elevenlabs_tts_model: str = "eleven_multilingual_v2"

    # ── Narration Voices (3-tier structure for 2–9 years) ────────────────────────
    # Primary Soothing: Main narrator – most calming & bedtime-friendly
    elevenlabs_voice_primary_female: str = ""
    elevenlabs_voice_primary_male: str = ""
    # Secondary Softer: Backup narrator – alternative & character voices
    elevenlabs_voice_secondary_female: str = ""
    elevenlabs_voice_secondary_male: str = ""
    # Child Dialogue: Character & dialogue voices (use sparingly)
    elevenlabs_voice_child_female: str = ""
    elevenlabs_voice_child_male: str = ""

    # ── App ───────────────────────────────────────────────────
    app_env: str = "production"
    app_secret_key: str = "change-me"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    lan_host: str = ""
    tailscale_host: str = ""
    tailscale_path: str = ""
    audio_storage_dir: str = "./audio_files"
    story_storage_dir: str = "./stories"
    max_voice_recording_seconds: int = 300
    allowed_origins: str = "*"

    # ── Sentry ────────────────────────────────────────────────
    sentry_dsn: str = ""

    @property
    def preset_voices(self) -> dict[str, str]:
        """Map of voice slug → ElevenLabs voice ID (3-tier structure)."""
        return {
            # Primary tier: Main soothing narration
            "primary_female": self.elevenlabs_voice_primary_female,
            "primary_male": self.elevenlabs_voice_primary_male,
            # Secondary tier: Backup & alternative narration
            "secondary_female": self.elevenlabs_voice_secondary_female,
            "secondary_male": self.elevenlabs_voice_secondary_male,
            # Child tier: Character dialogue
            "child_female": self.elevenlabs_voice_child_female,
            "child_male": self.elevenlabs_voice_child_male,
        }

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    """Cached singleton – call this everywhere."""
    return Settings()
