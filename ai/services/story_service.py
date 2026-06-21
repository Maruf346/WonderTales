"""
services/story_service.py
──────────────────────────
Handles all OpenAI calls:
  • generate_story()    – brand-new story
  • continue_story()    – continuation of existing story

Uses tenacity for automatic retry on transient failures.
"""

from __future__ import annotations

from openai import AsyncOpenAI, APIError, APITimeoutError, RateLimitError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from core.config import get_settings
from core.exceptions import StoryGenerationError
from core.logging import logger
from models.schemas import ChildProfile, Language, StoryTheme


_RETRY_EXCEPTIONS = (APIError, APITimeoutError, RateLimitError)

settings = get_settings()
_client = AsyncOpenAI(api_key=settings.openai_api_key)


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


def _new_story_prompt(
    child: ChildProfile,
    language: Language,
    theme: StoryTheme,
    custom_theme: str | None,
) -> str:
    theme_label = custom_theme if (theme == StoryTheme.custom and custom_theme) else theme.value
    interests = ", ".join(child.interests) if child.interests else "general adventures"

    return (
        f"Write Chapter 1 of a bedtime story for {child.name}, who is {child.age} years old "
        f"and loves {interests}. "
        f"Theme: {theme_label}. "
        f"Language: {language.value}. "
        f"Length: approximately 300–450 words. "
        f"Tone: soothing, imaginative, age-appropriate for a {child.age}-year-old. "
        f"Age guidance: {_age_story_direction(child.age)} "
        f"Theme guidance: {_theme_story_direction(theme, custom_theme)} "
        f"Make this story feel distinct from other stories: use a different opening, a unique small adventure, and varied pacing. "
        f"Do not reuse familiar phrases or repeated sentence patterns unless they clearly fit the scene. "
        f"End this chapter with a soft pause or gentle cliffhanger that leaves room for the story to continue."
    )


def _continuation_prompt(
    child: ChildProfile,
    previous_text: str,
    language: Language,
) -> str:
    return (
        f"Write the NEXT chapter of the following story for {child.name} (age {child.age}). "
        f"Seamlessly pick up where the previous chapters left off. "
        f"Language: {language.value}. "
        f"Length: approximately 250–350 words. "
        f"Maintain the same tone and characters. "
        f"Age guidance: {_age_story_direction(child.age)} "
        f"Theme guidance: preserve the established theme, mood, and pacing of the existing story. "
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
async def _call_openai(system: str, user: str) -> str:
    """Raw OpenAI call with retry logic."""
    response = await _client.chat.completions.create(
        model=settings.openai_model,
        max_tokens=settings.openai_max_tokens,
        temperature=settings.openai_temperature,
        presence_penalty=settings.openai_presence_penalty,
        frequency_penalty=settings.openai_frequency_penalty,
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
        logger.info("story.generate", child=child.name, age=child.age, theme=theme)
        text = await _call_openai(
            system=_system_prompt(),
            user=_new_story_prompt(child, language, theme, custom_theme),
        )
        logger.info("story.generate.ok", chars=len(text))
        return text
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
        logger.info("story.continue", child=child.name)
        text = await _call_openai(
            system=_system_prompt(),
            user=_continuation_prompt(child, previous_text, language),
        )
        logger.info("story.continue.ok", chars=len(text))
        return text
    except Exception as exc:
        logger.error("story.continue.failed", error=str(exc))
        raise StoryGenerationError(str(exc)) from exc
