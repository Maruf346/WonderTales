import requests
from django.core.files.base import ContentFile
import os

# Base URL for the AI microservice. Adjust as needed for production.
AI_BASE_URL = os.environ.get('AI_BASE_URL', 'http://localhost:8050')

def generate_story_from_ai(child_name, child_age, interests, language, narrator_voice, theme, cloned_voice_id=None):
    # Normalize language (e.g., 'english' -> 'en')
    language_map = {
        "english": "en", "french": "fr", "spanish": "es", "arabic": "ar",
        "hindi": "hi", "german": "de", "portuguese": "pt"
    }
    lang_code = language_map.get(language.lower(), language.lower())

    # Handle theme enums vs custom themes
    allowed_themes = ["adventure", "fantasy", "animals", "science", "friendship", "bedtime", "custom"]
    
    # Fix common typo
    if theme.lower() == "advanture":
        theme = "adventure"
        
    ai_theme = theme.lower()
    custom_theme = None
    if ai_theme not in allowed_themes:
        custom_theme = theme
        ai_theme = "custom"

    payload = {
        "child_profile": {
            "name": child_name,
            "age": child_age,
            "interests": interests
        },
        "language": lang_code,
        "narrator_voice": narrator_voice,
        "theme": ai_theme
    }
    
    if custom_theme:
        payload["custom_theme"] = custom_theme
    if cloned_voice_id:
        payload["cloned_voice_id"] = cloned_voice_id

    response = requests.post(f"{AI_BASE_URL}/stories/generate", json=payload)
    if response.status_code == 422:
        raise Exception(f"AI Validation Error: {response.text}")
    response.raise_for_status()
    return response.json()

def continue_story_from_ai(child_name, child_age, interests, language, narrator_voice, story_id, cloned_voice_id=None, previous_text=None):
    # Normalize language
    language_map = {
        "english": "en", "french": "fr", "spanish": "es", "arabic": "ar",
        "hindi": "hi", "german": "de", "portuguese": "pt"
    }
    lang_code = language_map.get(language.lower(), language.lower())

    payload = {
        "child_profile": {
            "name": child_name,
            "age": child_age,
            "interests": interests
        },
        "language": lang_code,
        "narrator_voice": narrator_voice,
        "story_id": story_id
    }
    if previous_text:
        payload["previous_story_text"] = previous_text
    if cloned_voice_id:
        payload["cloned_voice_id"] = cloned_voice_id

    response = requests.post(f"{AI_BASE_URL}/stories/continue", json=payload)
    if response.status_code == 422:
        raise Exception(f"AI Validation Error: {response.text}")
    response.raise_for_status()
    return response.json()

def clone_voice_via_ai(voice_name, description, audio_file):
    files = {
        'audio_file': (audio_file.name, audio_file.read(), audio_file.content_type)
    }
    data = {
        'voice_name': voice_name,
        'description': description
    }
    response = requests.post(f"{AI_BASE_URL}/voices/clone", data=data, files=files)
    response.raise_for_status()
    return response.json()

def download_audio(audio_url):
    response = requests.get(audio_url)
    response.raise_for_status()
    return ContentFile(response.content)
