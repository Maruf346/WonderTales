import os
import unittest

os.environ.setdefault("OPENAI_API_KEY", "test-openai-key")
os.environ.setdefault("ELEVENLABS_API_KEY", "test-elevenlabs-key")

from services import moderation_service


class TestModerationFalsePositives(unittest.TestCase):
    def test_safe_words_with_sensitive_substrings(self):
        self.assertTrue(moderation_service.is_safe_output("A classical melody floated above the lake."))
        self.assertTrue(moderation_service.is_safe_output("The assistant owl carried a lantern."))
        self.assertTrue(moderation_service.is_safe_output("They crossed a passage under moonlight."))

    def test_safe_custom_theme_not_flagged(self):
        self.assertTrue(
            moderation_service.is_safe_input(
                interests=["painting", "reading"],
                custom_theme="adventure in a crystal cave",
                previous_story_text=None,
            )
        )

    def test_true_positive_still_blocked(self):
        self.assertFalse(moderation_service.is_safe_output("The villain planned a murder."))
        self.assertFalse(
            moderation_service.is_safe_input(
                interests=["space"],
                custom_theme="how to make drugs",
                previous_story_text=None,
            )
        )


if __name__ == "__main__":
    unittest.main()
