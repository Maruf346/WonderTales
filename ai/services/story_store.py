"""Simple JSON file storage for generated stories."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
import re

from core.config import get_settings


settings = get_settings()
_story_dir = Path(settings.story_storage_dir)
_story_dir.mkdir(parents=True, exist_ok=True)


def create_story_id() -> str:
    return uuid4().hex


def story_path(story_id: str) -> Path:
    return _story_dir / f"{story_id}.json"


def save_story_record(record: dict) -> dict:
    raw_id = record.get("story_id")
    # treat placeholder values like 'string', 'null', or repeated 'stringstring' as missing
    if isinstance(raw_id, str):
        low = re.sub(r"\s+", "", raw_id.lower())
        if low in {"", "string", "null"} or re.fullmatch(r"(?:string)+", low):
            story_id = create_story_id()
        else:
            story_id = raw_id
    else:
        story_id = create_story_id()
    payload = {
        **record,
        "story_id": story_id,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    path = story_path(story_id)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def load_story_record(story_id: str) -> dict:
    path = story_path(story_id)
    if not path.exists():
        raise FileNotFoundError(f"Story '{story_id}' not found")
    return json.loads(path.read_text(encoding="utf-8"))
