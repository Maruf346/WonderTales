"""Simple JSON-backed store for cloned ElevenLabs voices."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

from core.config import get_settings
from core.logging import logger

settings = get_settings()
# Store cloned voices alongside the `stories` directory to avoid cwd issues
VOICE_STORE_FILE = Path(settings.story_storage_dir).parent / "cloned_voices.json"
VOICE_STORE_FILE.parent.mkdir(parents=True, exist_ok=True)


def _read_store() -> list[Dict[str, Any]]:
    if not VOICE_STORE_FILE.exists():
        return []
    try:
        return json.loads(VOICE_STORE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def _write_store(data: list[Dict[str, Any]]) -> None:
    """Write voice store to JSON file with explicit sync."""
    try:
        json_content = json.dumps(data, ensure_ascii=False, indent=2)
        VOICE_STORE_FILE.write_text(json_content, encoding="utf-8")
        # Ensure data is flushed to disk
        VOICE_STORE_FILE.stat()  # Force OS to sync
        logger.debug("voice_store.written", path=str(VOICE_STORE_FILE), voices_count=len(data))
    except Exception as exc:
        logger.error("voice_store.write_failed", error=str(exc), path=str(VOICE_STORE_FILE))
        raise


def save_cloned_voice(voice_id: str, voice_name: str, description: str | None = None) -> Dict[str, Any]:
    """Persist a cloned voice record and return the record."""
    record = {
        "voice_id": voice_id,
        "voice_name": voice_name,
        "description": description,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    data = _read_store()
    # avoid duplicates
    if any(r.get("voice_id") == voice_id for r in data):
        logger.info("voice_store.duplicate_skipped", voice_id=voice_id, voice_name=voice_name)
        return record
    
    data.append(record)
    _write_store(data)
    logger.info("voice_store.saved", voice_id=voice_id, voice_name=voice_name, total_voices=len(data))
    return record


def list_cloned_voices() -> list[Dict[str, Any]]:
    """Return all cloned voice records."""
    return _read_store()
