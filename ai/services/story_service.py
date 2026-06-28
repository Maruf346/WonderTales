"""
services/story_service.py
──────────────────────────
Handles all OpenAI calls:
  • generate_story()    – brand-new story
  • continue_story()    – continuation of existing story

Uses tenacity for automatic retry on transient failures.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import secrets

from openai import AsyncOpenAI, APIError, APITimeoutError, RateLimitError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from core.config import get_settings
from core.exceptions import InvalidInputError, StoryGenerationError
from core.logging import logger
from models.schemas import ChildProfile, Language, StoryTheme
from services import moderation_service


_RETRY_EXCEPTIONS = (APIError, APITimeoutError, RateLimitError)

settings = get_settings()
_client = AsyncOpenAI(api_key=settings.openai_api_key)


_OPENING_STYLES = [
    "start with a tiny, ordinary bedtime moment that becomes magical",
    "open mid-motion with the child already exploring a gentle mystery",
    "begin with a surprising sound, glow, or whisper that invites curiosity",
    "start with a warm dialogue line between two friendly characters",
    "open with a sensory image centered on moonlight, breeze, or soft footsteps",
]

_STRUCTURE_STYLES = [
    "three short scene beats (arrival, discovery, calm resolution)",
    "single flowing journey with one turning point",
    "nested mini-adventures that loop back to a comforting ending",
    "question-answer rhythm where each clue gently leads to the next",
    "paired scenes that mirror each other before the final calm",
]

_ENDING_STYLES = [
    "close with a quiet promise for tomorrow",
    "close with a sleepy image and a soft final line",
    "close with gratitude and a gentle exhale",
    "close with stars, moon, or night sounds settling everything",
    "close with a tiny unresolved wonder that still feels safe",
]

_THEME_VARIATION_GUIDANCE: dict[StoryTheme, list[str]] = {
    StoryTheme.adventure: [
        "focus on trail maps, landmarks, and step-by-step progress",
        "use playful stakes like delivering a message before starlight fades",
        "highlight brave but kind choices over speed or competition",
    ],
    StoryTheme.fantasy: [
        "center enchanted objects with specific rules",
        "use dreamlike locations that transform as emotions change",
        "feature a gentle magical mentor with unexpected wisdom",
    ],
    StoryTheme.animals: [
        "let animal habits drive the plot naturally",
        "build cozy community scenes in burrows, nests, or tree homes",
        "use light humor through animal misunderstandings and teamwork",
    ],
    StoryTheme.science: [
        "anchor wonder in experiments, observation, and discovery",
        "turn everyday objects into mini inventions",
        "use clear cause-and-effect moments with playful curiosity",
    ],
    StoryTheme.friendship: [
        "focus on listening, sharing, and repairing tiny conflicts",
        "show each friend contributing a different strength",
        "end with a shared ritual that deepens trust",
    ],
    StoryTheme.bedtime: [
        "use repetitive soothing motifs like lantern-light, blankets, and lullabies",
        "keep conflict minimal and emotionally soft",
        "let the final paragraphs gradually slow in rhythm and imagery",
    ],
    StoryTheme.custom: [
        "translate the custom theme into a clear mood arc",
        "ground the custom theme in concrete scene details",
        "keep one memorable symbol tied to the custom theme",
    ],
}

_STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in", "is", "it",
    "of", "on", "or", "that", "the", "this", "to", "was", "were", "with",
}


# ── Prompt builders ───────────────────────────────────────────────

def _system_prompt() -> str:
    return (
        "You are WonderTells, a master children's storyteller. "
        "You craft imaginative, warm, age-appropriate bedtime stories. "
        "Stories are engaging, positive, and always end on a calming, hopeful note. "
        "Never include violence, fear, adult themes, or inappropriate content. "
        "Vary sentence length for rhythm when read aloud. "
        "Avoid repeating the same opening phrases, stock transitions, or ending patterns across stories. "
        "Prefer fresh settings, new imagery, different character actions, and varied sentence structures each time. "
        "Return ONLY the story text – no titles, no markdown, no preamble."
    )


def _age_story_direction(age: int) -> str:
    if age <= 4:
        return (
            "Use very gentle, simple language with soft magical imagery, short scenes, "
            "and a calm, cozy bedtime feeling."
        )
    if age <= 7:
        return (
            "Use playful, colorful language with a light sense of adventure, friendly characters, "
            "and clear, easy-to-follow scenes."
        )
    if age <= 10:
        return (
            "Use a more adventurous tone with wonder, small challenges, and vivid settings, "
            "while keeping the story comforting and age-appropriate."
        )
    return (
        "Use rich but gentle language with slightly more varied pacing, meaningful choices, "
        "and a mature bedtime calm that still feels warm and safe."
    )


def _theme_story_direction(theme: StoryTheme, custom_theme: str | None) -> str:
    if theme == StoryTheme.adventure:
        return (
            "Use a more energetic pace, clear forward motion, and a sense of discovery or small quest-like progress."
        )
    if theme == StoryTheme.fantasy:
        return (
            "Use magical imagery, gentle wonder, and a dreamy, enchanted mood."
        )
    if theme == StoryTheme.animals:
        return (
            "Use warm, cozy scenes, gentle humor, and expressive animal behavior that feels charming and comforting."
        )
    if theme == StoryTheme.science:
        return (
            "Use curious, inventive, and exploratory pacing with wonder about how things work."
        )
    if theme == StoryTheme.friendship:
        return (
            "Use heartfelt, supportive, and emotionally warm pacing that highlights caring and cooperation."
        )
    if theme == StoryTheme.bedtime:
        return (
            "Use a slow, soothing, lullaby-like rhythm with soft transitions and a sleepy ending."
        )
    if theme == StoryTheme.custom and custom_theme:
        return f"Match the custom theme '{custom_theme}' with a mood, pacing, and imagery that clearly fit it."
    return "Vary the pacing and mood so the theme feels distinct from other stories."


def _first_n_words(text: str, n: int = 12) -> str:
    words = re.findall(r"\b[\w']+\b", text)
    return " ".join(words[:n])


def _last_n_words(text: str, n: int = 12) -> str:
    words = re.findall(r"\b[\w']+\b", text)
    return " ".join(words[-n:])


def _recent_story_signals(limit: int = 6) -> tuple[list[str], list[str]]:
    story_dir = Path(settings.story_storage_dir)
    if not story_dir.exists():
        return [], []

    files = sorted(story_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    recent_files = files[:limit]

    opening_samples: list[str] = []
    ending_samples: list[str] = []

    for file_path in recent_files:
        try:
            record = json.loads(file_path.read_text(encoding="utf-8"))
            text = (record.get("latest_segment_text") or record.get("story_text") or "").strip()
            if not text:
                continue
            opening = _first_n_words(text)
            ending = _last_n_words(text)
            if opening:
                opening_samples.append(opening)
            if ending:
                ending_samples.append(ending)
        except Exception:
            continue

    return opening_samples[:3], ending_samples[:3]


def _variation_brief(theme: StoryTheme, custom_theme: str | None) -> str:
    theme_options = _THEME_VARIATION_GUIDANCE.get(theme, _THEME_VARIATION_GUIDANCE[StoryTheme.custom])
    theme_focus = secrets.choice(theme_options)
    opening_style = secrets.choice(_OPENING_STYLES)
    structure_style = secrets.choice(_STRUCTURE_STYLES)
    ending_style = secrets.choice(_ENDING_STYLES)
    creativity_nonce = secrets.token_hex(4)

    custom_focus = ""
    if theme == StoryTheme.custom and custom_theme:
        custom_focus = (
            f" For this custom theme, keep '{custom_theme}' explicit in setting, character goal, and final emotional beat."
        )

    return (
        "Use this creative brief for variety (do not copy these bullets verbatim into the output): "
        f"opening style = {opening_style}; "
        f"story structure = {structure_style}; "
        f"theme focus = {theme_focus}; "
        f"ending style = {ending_style}; "
        f"variation id = {creativity_nonce}."
        f"{custom_focus}"
    )


def _recent_story_texts(limit: int = 8) -> list[str]:
    story_dir = Path(settings.story_storage_dir)
    if not story_dir.exists():
        return []

    files = sorted(story_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    recent_files = files[:limit]

    texts: list[str] = []
    for file_path in recent_files:
        try:
            record = json.loads(file_path.read_text(encoding="utf-8"))
            text = (record.get("latest_segment_text") or record.get("story_text") or "").strip()
            if text:
                texts.append(text)
        except Exception:
            continue
    return texts


def _keyword_set(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z']+", text.lower())
    return {w for w in words if len(w) > 2 and w not in _STOP_WORDS}


def _jaccard_similarity(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    intersection = a.intersection(b)
    union = a.union(b)
    if not union:
        return 0.0
    return len(intersection) / len(union)


def _max_similarity_to_recent(text: str, limit: int = 8) -> float:
    candidate = _keyword_set(text)
    if not candidate:
        return 0.0

    max_similarity = 0.0
    for recent in _recent_story_texts(limit=limit):
        score = _jaccard_similarity(candidate, _keyword_set(recent))
        if score > max_similarity:
            max_similarity = score
    return max_similarity


def _new_story_prompt(
    child: ChildProfile,
    language: Language,
    theme: StoryTheme,
    custom_theme: str | None,
) -> str:
    theme_label = custom_theme if (theme == StoryTheme.custom and custom_theme) else theme.value
    interests = ", ".join(child.interests) if child.interests else "general adventures"
    opening_samples, ending_samples = _recent_story_signals()

    anti_repeat_guidance = ""
    if opening_samples:
        anti_repeat_guidance += (
            " Avoid openings that feel too close to these recent starts: "
            f"{'; '.join(opening_samples)}."
        )
    if ending_samples:
        anti_repeat_guidance += (
            " Avoid ending with patterns too similar to these recent endings: "
            f"{'; '.join(ending_samples)}."
        )

    return (
        f"Write Chapter 1 of a bedtime story for {child.name}, who is {child.age} years old "
        f"and loves {interests}. "
        f"Theme: {theme_label}. "
        f"Language: {language.value}. "
        f"Length: approximately 300–450 words. "
        f"Tone: soothing, imaginative, age-appropriate for a {child.age}-year-old. "
        f"Age guidance: {_age_story_direction(child.age)} "
        f"Theme guidance: {_theme_story_direction(theme, custom_theme)} "
        f"Variation guidance: {_variation_brief(theme, custom_theme)} "
        f"Make this story feel distinct from other stories: use a different opening, a unique small adventure, and varied pacing. "
        f"Do not reuse familiar phrases or repeated sentence patterns unless they clearly fit the scene. "
        f"{anti_repeat_guidance} "
        f"End this chapter with a soft pause or gentle cliffhanger that leaves room for the story to continue."
    )


def _continuation_prompt(
    child: ChildProfile,
    previous_text: str,
    language: Language,
) -> str:
    continuation_brief = (
        "Use a fresh chapter transition and avoid repetitive openers like 'The next day' or 'Suddenly'. "
        f"Pick a new pacing pattern and image focus for this continuation. variation id = {secrets.token_hex(4)}."
    )

    return (
        f"Write the NEXT chapter of the following story for {child.name} (age {child.age}). "
        f"Seamlessly pick up where the previous chapters left off. "
        f"Language: {language.value}. "
        f"Length: approximately 250–350 words. "
        f"Maintain the same tone and characters. "
        f"Age guidance: {_age_story_direction(child.age)} "
        f"Theme guidance: preserve the established theme, mood, and pacing of the existing story. "
        f"Variation guidance: {continuation_brief} "
        f"End with a satisfying, sleepy conclusion or another gentle pause.\n\n"
        f"PREVIOUS CHAPTERS:\n{previous_text}"
    )


# ── Service functions ─────────────────────────────────────────────

@retry(
    retry=retry_if_exception_type(_RETRY_EXCEPTIONS),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=False,
)
async def _call_openai(
    system: str,
    user: str,
    temperature: float | None = None,
    presence_penalty: float | None = None,
    frequency_penalty: float | None = None,
) -> str:
    """Raw OpenAI call with retry logic."""
    response = await _client.chat.completions.create(
        model=settings.openai_model,
        max_tokens=settings.openai_max_tokens,
        temperature=settings.openai_temperature if temperature is None else temperature,
        presence_penalty=settings.openai_presence_penalty if presence_penalty is None else presence_penalty,
        frequency_penalty=settings.openai_frequency_penalty if frequency_penalty is None else frequency_penalty,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return response.choices[0].message.content.strip()


async def generate_story(
    child: ChildProfile,
    language: Language,
    theme: StoryTheme,
    custom_theme: str | None = None,
) -> str:
    """Generate a brand-new story. Returns story text."""
    try:
        if not moderation_service.is_safe_input(
            interests=child.interests,
            custom_theme=custom_theme,
            previous_story_text=None,
        ):
            raise InvalidInputError(
                "Input contains content that is not allowed for child-safe stories."
            )

        logger.info("story.generate", child=child.name, age=child.age, theme=theme)

        regen_attempts = max(0, settings.story_moderation_regen_attempts)
        attempts = max(1, settings.story_diversity_max_attempts) + regen_attempts
        threshold = settings.story_diversity_similarity_threshold
        best_text = ""
        best_similarity = 1.0
        found_safe = False

        for attempt in range(attempts):
            temperature = min(1.15, settings.openai_temperature + (attempt * 0.07))
            presence_penalty = min(1.1, settings.openai_presence_penalty + (attempt * 0.05))
            frequency_penalty = min(1.1, settings.openai_frequency_penalty + (attempt * 0.05))

            text = await _call_openai(
                system=_system_prompt(),
                user=_new_story_prompt(child, language, theme, custom_theme),
                temperature=temperature,
                presence_penalty=presence_penalty,
                frequency_penalty=frequency_penalty,
            )

            if not moderation_service.is_safe_output(text):
                logger.info(
                    "story.generate.retry_for_moderation",
                    attempt=attempt + 1,
                )
                continue

            found_safe = True

            similarity = _max_similarity_to_recent(text)
            if similarity < best_similarity:
                best_similarity = similarity
                best_text = text

            if similarity <= threshold:
                logger.info(
                    "story.generate.ok",
                    chars=len(text),
                    similarity=round(similarity, 4),
                    threshold=threshold,
                    attempt=attempt + 1,
                )
                return text

            logger.info(
                "story.generate.retry_for_diversity",
                attempt=attempt + 1,
                similarity=round(similarity, 4),
                threshold=threshold,
            )

        if not found_safe:
            raise StoryGenerationError(
                "Generated content failed child-safety checks. Please try again."
            )

        logger.info(
            "story.generate.ok.best_effort",
            chars=len(best_text),
            similarity=round(best_similarity, 4),
            threshold=threshold,
            attempts=attempts,
        )
        return best_text
    except InvalidInputError:
        raise
    except Exception as exc:
        logger.error("story.generate.failed", error=str(exc))
        raise StoryGenerationError(str(exc)) from exc


async def continue_story(
    child: ChildProfile,
    previous_text: str,
    language: Language,
) -> str:
    """Continue an existing story. Returns continuation text only."""
    try:
        if not moderation_service.is_safe_input(
            interests=child.interests,
            custom_theme=None,
            previous_story_text=previous_text,
        ):
            raise InvalidInputError(
                "Input contains content that is not allowed for child-safe stories."
            )

        logger.info("story.continue", child=child.name)
        attempts = 1 + max(0, settings.story_moderation_regen_attempts)
        text = ""

        for attempt in range(attempts):
            candidate = await _call_openai(
                system=_system_prompt(),
                user=_continuation_prompt(child, previous_text, language),
            )

            if moderation_service.is_safe_output(candidate):
                text = candidate
                break

            logger.info(
                "story.continue.retry_for_moderation",
                attempt=attempt + 1,
            )

        if not text:
            raise StoryGenerationError(
                "Generated continuation failed child-safety checks. Please try again."
            )

        logger.info("story.continue.ok", chars=len(text))
        return text
    except InvalidInputError:
        raise
    except Exception as exc:
        logger.error("story.continue.failed", error=str(exc))
        raise StoryGenerationError(str(exc)) from exc
