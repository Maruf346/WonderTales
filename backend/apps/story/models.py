from django.db import models
from apps.users.models import ChildrenProfileModel, CustomUserModel

class VoiceCloneModel(models.Model):
    """
    Stores cloned voices from ElevenLabs for a specific user.
    """
    user = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE, related_name='cloned_voices')
    voice_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    voice_id_ai = models.CharField(max_length=255) # voice_id returned from ElevenLabs
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.voice_name

class LanguageChoices(models.TextChoices):
    ENGLISH = 'en', 'English'
    FRENCH = 'fr', 'French'
    SPANISH = 'es', 'Spanish'
    ARABIC = 'ar', 'Arabic'
    HINDI = 'hi', 'Hindi'
    GERMAN = 'de', 'German'
    PORTUGUESE = 'pt', 'Portuguese'

class ThemeChoices(models.TextChoices):
    ADVENTURE = 'adventure', 'Adventure'
    FANTASY = 'fantasy', 'Fantasy'
    ANIMALS = 'animals', 'Animals'
    SCIENCE = 'science', 'Science'
    FRIENDSHIP = 'friendship', 'Friendship'
    BEDTIME = 'bedtime', 'Bedtime'
    CUSTOM = 'custom', 'Custom'

class VoiceChoices(models.TextChoices):
    PRIMARY_FEMALE = 'primary_female', 'Primary Female'
    PRIMARY_MALE = 'primary_male', 'Primary Male'
    SECONDARY_FEMALE = 'secondary_female', 'Secondary Female'
    SECONDARY_MALE = 'secondary_male', 'Secondary Male'
    CHILD_FEMALE = 'child_female', 'Child Female'
    CHILD_MALE = 'child_male', 'Child Male'

class StoryModel(models.Model):
    """
    This model is used to store the stories.
    """
    children_profile = models.ForeignKey(ChildrenProfileModel, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, null=True)
    length = models.IntegerField(blank=True, null=True)
    theme = models.CharField(max_length=50, choices=ThemeChoices.choices, default=ThemeChoices.BEDTIME)
    custom_theme = models.CharField(max_length=200, blank=True, null=True)
    full_story = models.TextField(blank=True, null=True)
    language = models.CharField(max_length=10, choices=LanguageChoices.choices, default=LanguageChoices.ENGLISH)
    selected_voices = models.CharField(max_length=50, choices=VoiceChoices.choices, default=VoiceChoices.PRIMARY_FEMALE)
    
    # New fields for AI integration
    cloned_voice_id = models.CharField(max_length=255, blank=True, null=True) # If using a custom cloned voice
    story_id_ai = models.CharField(max_length=255, blank=True, null=True) # to continue stories
    audio_file = models.FileField(upload_to='stories/audio/', blank=True, null=True)
    word_timestamps = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title or f"Story for {self.children_profile}"

class StoryChapterModel(models.Model):
    """
    Stores individual chapters for a story.
    """
    story = models.ForeignKey(StoryModel, on_delete=models.CASCADE, related_name='chapters')
    chapter_number = models.IntegerField(default=1)
    text = models.TextField(blank=True, null=True)
    audio_file = models.FileField(upload_to='stories/chapters/audio/', blank=True, null=True)
    word_timestamps = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['chapter_number']

    def __str__(self):
        return f"{self.story} - Chapter {self.chapter_number}"
