"""
services/moderation_service.py
──────────────────────────────
Lightweight safety moderation for story inputs and outputs.

This module is intentionally conservative and deterministic so it can run
without additional provider calls and without changing core API contracts.
"""

from __future__ import annotations

import re

from core.config import get_settings

settings = get_settings()

# Keep this list small and explicit to reduce false positives.
_BANNED_PATTERNS = [
    r"\b(kill|murder|stab|shoot|weapon|blood|gore)\b",
    r"\b(sex|sexual|nude|porn|adult\s+content)\b",
    r"\b(suicide|self\s*harm|harm\s+yourself)\b",
    r"\b(abuse|assault|torture)\b",
    r"\b(hate\s+speech|racist|sexist|slur)\b",
    r"\b(drugs?|cocaine|heroin|meth)\b",
]


def _normalize(text: str | None) -> str:
    return (text or "").strip().lower()


def _contains_unsafe_content(text: str | None) -> bool:
    normalized = _normalize(text)
    if not normalized:
        return False

    for pattern in _BANNED_PATTERNS:
        if re.search(pattern, normalized, flags=re.IGNORECASE):
            return True
    return False


def is_enabled() -> bool:
    return settings.story_moderation_enabled


def is_safe_input(*, interests: list[str], custom_theme: str | None, previous_story_text: str | None) -> bool:
    if not is_enabled():
        return True

    joined_interests = " ".join(interests or [])
    return not any(
        [
            _contains_unsafe_content(joined_interests),
            _contains_unsafe_content(custom_theme),
            _contains_unsafe_content(previous_story_text),
        ]
    )


def is_safe_output(story_text: str) -> bool:
    if not is_enabled():
        return True
    return not _contains_unsafe_content(story_text)
