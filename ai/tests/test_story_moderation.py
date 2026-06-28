import os
import unittest
from unittest.mock import AsyncMock, patch

os.environ.setdefault("OPENAI_API_KEY", "test-openai-key")
os.environ.setdefault("ELEVENLABS_API_KEY", "test-elevenlabs-key")

from core.exceptions import InvalidInputError, StoryGenerationError
from models.schemas import ChildProfile, Language, StoryTheme
from services import moderation_service, story_service


class TestModerationService(unittest.TestCase):
    def test_safe_input_passes(self):
        self.assertTrue(
            moderation_service.is_safe_input(
                interests=["stars", "dinosaurs"],
                custom_theme="gentle moon journey",
                previous_story_text=None,
            )
        )

    def test_unsafe_input_fails(self):
        self.assertFalse(
            moderation_service.is_safe_input(
                interests=["space", "how to kill dragons"],
                custom_theme=None,
                previous_story_text=None,
            )
        )

    def test_unsafe_output_fails(self):
        self.assertFalse(moderation_service.is_safe_output("The hero used a weapon."))


class TestStoryServiceModerationFlow(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.child = ChildProfile(name="Amara", age=6, interests=["space", "owls"])

    async def test_generate_story_blocks_unsafe_input(self):
        with patch("services.story_service.moderation_service.is_safe_input", return_value=False):
            with self.assertRaises(InvalidInputError):
                await story_service.generate_story(
                    child=self.child,
                    language=Language.english,
                    theme=StoryTheme.bedtime,
                    custom_theme="safe",
                )

    async def test_generate_story_regenerates_once_when_first_output_unsafe(self):
        with patch("services.story_service.moderation_service.is_safe_input", return_value=True), patch(
            "services.story_service.moderation_service.is_safe_output", side_effect=[False, True]
        ), patch(
            "services.story_service._call_openai",
            new=AsyncMock(side_effect=["unsafe draft with weapon", "A calm and cozy bedtime story."]),
        ) as mocked_openai:
            text = await story_service.generate_story(
                child=self.child,
                language=Language.english,
                theme=StoryTheme.bedtime,
                custom_theme=None,
            )

            self.assertEqual(text, "A calm and cozy bedtime story.")
            self.assertEqual(mocked_openai.await_count, 2)

    async def test_generate_story_raises_when_all_outputs_unsafe(self):
        attempts = max(1, story_service.settings.story_diversity_max_attempts) + max(
            0, story_service.settings.story_moderation_regen_attempts
        )

        with patch("services.story_service.moderation_service.is_safe_input", return_value=True), patch(
            "services.story_service.moderation_service.is_safe_output", return_value=False
        ), patch(
            "services.story_service._call_openai",
            new=AsyncMock(return_value="unsafe draft with violence"),
        ) as mocked_openai:
            with self.assertRaises(StoryGenerationError):
                await story_service.generate_story(
                    child=self.child,
                    language=Language.english,
                    theme=StoryTheme.bedtime,
                    custom_theme=None,
                )

            self.assertEqual(mocked_openai.await_count, attempts)

    async def test_continue_story_blocks_unsafe_previous_text(self):
        with patch("services.story_service.moderation_service.is_safe_input", return_value=False):
            with self.assertRaises(InvalidInputError):
                await story_service.continue_story(
                    child=self.child,
                    previous_text="unsafe previous story",
                    language=Language.english,
                )

    async def test_continue_story_regenerates_once_for_unsafe_output(self):
        with patch("services.story_service.moderation_service.is_safe_input", return_value=True), patch(
            "services.story_service.moderation_service.is_safe_output", side_effect=[False, True]
        ), patch(
            "services.story_service._call_openai",
            new=AsyncMock(side_effect=["unsafe continuation", "Safe continuation chapter."]),
        ) as mocked_openai:
            text = await story_service.continue_story(
                child=self.child,
                previous_text="A safe chapter one.",
                language=Language.english,
            )

            self.assertEqual(text, "Safe continuation chapter.")
            self.assertEqual(mocked_openai.await_count, 2)


if __name__ == "__main__":
    unittest.main()
