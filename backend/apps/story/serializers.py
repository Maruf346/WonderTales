from rest_framework import serializers
from apps.story.models import StoryModel, StoryChapterModel, VoiceCloneModel

class VoiceCloneModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoiceCloneModel
        fields = ['id', 'user', 'voice_name', 'description', 'voice_id_ai', 'created_at']
        read_only_fields = ['id', 'user', 'voice_id_ai', 'created_at']

class StoryChapterModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoryChapterModel
        fields = ['id', 'chapter_number', 'text', 'audio_file', 'word_timestamps', 'created_at']
        read_only_fields = ['id', 'created_at']

class StoryModelSerializer(serializers.ModelSerializer):
    chapters = StoryChapterModelSerializer(many=True, read_only=True)

    class Meta:
        model = StoryModel
        fields = [
            'id', 'children_profile', 'title', 'length', 'theme', 'custom_theme',
            'full_story', 'language', 'selected_voices', 'cloned_voice_id',
            'story_id_ai', 'audio_file', 'word_timestamps', 'created_at', 'updated_at', 'chapters'
        ]
        read_only_fields = ['id', 'story_id_ai', 'audio_file', 'word_timestamps', 'created_at', 'updated_at']

# Serializers for Swagger Request Body Documentation
class StoryGenerateRequestSerializer(serializers.Serializer):
    children_profile = serializers.IntegerField(help_text="ID of the children profile")
    title = serializers.CharField(max_length=255, required=False)
    length = serializers.IntegerField(required=False)
    theme = serializers.CharField(max_length=50, help_text="Theme of the story")
    custom_theme = serializers.CharField(max_length=200, required=False)
    language = serializers.CharField(max_length=10, default='en')
    narrator_voice = serializers.CharField(max_length=50, default='primary_female')
    cloned_voice_id = serializers.CharField(max_length=255, required=False)

class StoryContinueRequestSerializer(serializers.Serializer):
    narrator_voice = serializers.CharField(max_length=50, required=False)
    cloned_voice_id = serializers.CharField(max_length=255, required=False)

class VoiceCloneRequestSerializer(serializers.Serializer):
    voice_name = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=255, required=False)
    audio_file = serializers.FileField(help_text="MP3/WAV/M4A file to clone")