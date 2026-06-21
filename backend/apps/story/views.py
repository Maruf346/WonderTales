from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, parsers
from apps.story.models import StoryModel, VoiceCloneModel, StoryChapterModel
from apps.story.serializers import (
    StoryModelSerializer, VoiceCloneModelSerializer, StoryChapterModelSerializer,
    StoryGenerateRequestSerializer, StoryContinueRequestSerializer, VoiceCloneRequestSerializer
)
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from apps.users.models import ChildrenProfileModel
from .services import generate_story_from_ai, continue_story_from_ai, clone_voice_via_ai, download_audio
from drf_yasg.utils import swagger_auto_schema

class VoiceCloneViewSet(ModelViewSet):
    queryset = VoiceCloneModel.objects.all()
    serializer_class = VoiceCloneModelSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return self.queryset.none()
        return self.queryset.filter(user=self.request.user)

    @swagger_auto_schema(request_body=VoiceCloneRequestSerializer)
    @action(detail=False, methods=['post'], url_path='clone')
    def clone(self, request):
        voice_name = request.data.get('voice_name')
        description = request.data.get('description', '')
        audio_file = request.FILES.get('audio_file')
        
        if not all([voice_name, audio_file]):
            return Response({"error": "voice_name and audio_file are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Call AI microservice to clone voice
            ai_data = clone_voice_via_ai(voice_name, description, audio_file)
            voice_id_ai = ai_data.get('voice_id')
            
            # Save to database
            voice_clone = VoiceCloneModel.objects.create(
                user=request.user,
                voice_name=voice_name,
                description=description,
                voice_id_ai=voice_id_ai
            )
            serializer = self.get_serializer(voice_clone)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StoryModelViewSet(ModelViewSet):
    queryset = StoryModel.objects.all()
    serializer_class = StoryModelSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return self.queryset.none()
        return self.queryset.filter(children_profile__user=self.request.user)

    @swagger_auto_schema(request_body=StoryGenerateRequestSerializer)
    @action(detail=False, methods=['post'])
    def generate(self, request):
        # ...
        child_profile_id = request.data.get('children_profile')
        theme = request.data.get('theme')
        custom_theme = request.data.get('custom_theme')
        title = request.data.get('title')
        length = request.data.get('length')
        language = request.data.get('language', 'en')
        narrator_voice = request.data.get('narrator_voice', 'primary_female')
        cloned_voice_id = request.data.get('cloned_voice_id') # optional
        
        child_profile = get_object_or_404(ChildrenProfileModel, id=child_profile_id, user=request.user)
        
        interests = [i.strip() for i in child_profile.favourite_themes.split(',')] if child_profile.favourite_themes else []

        try:
            # Call AI microservice
            ai_data = generate_story_from_ai(
                child_name=child_profile.child_name,
                child_age=child_profile.child_age,
                interests=interests,
                language=language,
                narrator_voice=narrator_voice,
                theme=theme,
                cloned_voice_id=cloned_voice_id
            )
            
            # Download audio and create story record
            story = StoryModel(
                children_profile=child_profile,
                title=title,
                length=length,
                theme=theme,
                custom_theme=custom_theme,
                language=language,
                selected_voices=narrator_voice,
                cloned_voice_id=cloned_voice_id,
                full_story=ai_data.get('story_text'),
                story_id_ai=ai_data.get('story_id'),
                word_timestamps=ai_data.get('word_timestamps')
            )
            
            audio_url = ai_data.get('audio_url')
            if audio_url:
                audio_content = download_audio(audio_url)
                story.audio_file.save(f"story_{story.story_id_ai}.mp3", audio_content, save=False)
                
            story.save()

            # Create Chapter 1
            chapter = StoryChapterModel(
                story=story,
                chapter_number=1,
                text=ai_data.get('story_text'),
                word_timestamps=ai_data.get('word_timestamps')
            )
            if audio_url:
                chapter.audio_file.save(f"story_{story.story_id_ai}_chapter_1.mp3", audio_content, save=False)
            chapter.save()

            # Also populate full_story for backward compatibility
            story.full_story = chapter.text
            story.save()

            # Return the story envelope + the newly created chapter
            chapter_serializer = StoryChapterModelSerializer(chapter)
            return Response({
                "story_id": story.id,
                "story_id_ai": story.story_id_ai,
                "title": story.title,
                "theme": story.theme,
                "language": story.language,
                "current_chapter": chapter_serializer.data,
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(request_body=StoryContinueRequestSerializer)
    @action(detail=True, methods=['post'])
    def continue_story(self, request, pk=None):
        story = self.get_object()
        child_profile = story.children_profile
        narrator_voice = request.data.get('narrator_voice', story.selected_voices)
        cloned_voice_id = request.data.get('cloned_voice_id')
        
        interests = [i.strip() for i in child_profile.favourite_themes.split(',')] if child_profile.favourite_themes else []

        try:
            # First, fetch all chapters text to send to AI
            chapters = list(story.chapters.all().order_by('chapter_number'))
            if chapters:
                chapters_text = "\n\n".join([f"Chapter {c.chapter_number}:\n{c.text}" for c in chapters])
                next_chapter_num = chapters[-1].chapter_number + 1
            else:
                chapters_text = story.full_story or ""
                next_chapter_num = 2

            ai_data = continue_story_from_ai(
                child_name=child_profile.child_name,
                child_age=child_profile.child_age,
                interests=interests,
                language=story.language,
                narrator_voice=narrator_voice,
                story_id=story.story_id_ai,
                cloned_voice_id=cloned_voice_id,
                previous_text=chapters_text
            )
            
            # Create next chapter
            from apps.story.models import StoryChapterModel
            chapter = StoryChapterModel(
                story=story,
                chapter_number=next_chapter_num,
                text=ai_data.get('story_text'),
                word_timestamps=ai_data.get('word_timestamps')
            )
            
            # Update audio
            audio_url = ai_data.get('audio_url')
            if audio_url:
                audio_content = download_audio(audio_url)
                chapter.audio_file.save(f"story_{story.story_id_ai}_chapter_{next_chapter_num}.mp3", audio_content, save=False)
                
            chapter.save()

            # Update story's fallback fields
            if story.full_story:
                story.full_story += f"\n\n{chapter.text}"
            else:
                story.full_story = chapter.text
            story.word_timestamps = chapter.word_timestamps
            story.selected_voices = narrator_voice
            story.cloned_voice_id = cloned_voice_id
            story.save()

            # Return the story envelope + the newly created chapter
            chapter_serializer = StoryChapterModelSerializer(chapter)
            return Response({
                "story_id": story.id,
                "story_id_ai": story.story_id_ai,
                "title": story.title,
                "theme": story.theme,
                "language": story.language,
                "current_chapter": chapter_serializer.data,
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
