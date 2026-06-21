from django.contrib import admin
from unfold.admin import ModelAdmin
# from .models import StoryModel, VoiceCloneModel
# 
# @admin.register(StoryModel)
# class StoryAdmin(ModelAdmin):
#     list_display = ["title", "children_profile", "theme", "language", "created_at"]
#     list_filter = ["theme", "language", "created_at"]
#     search_fields = ["title", "children_profile__child_name", "full_story"]
#     readonly_fields = ["created_at", "updated_at"]
# 
# @admin.register(VoiceCloneModel)
# class VoiceCloneAdmin(ModelAdmin):
#     list_display = ["voice_name", "user", "voice_id_ai", "created_at"]
#     list_filter = ["created_at"]
#     search_fields = ["voice_name", "user__email", "voice_id_ai"]
