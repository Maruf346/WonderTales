from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import AppSettingsModel

@admin.register(AppSettingsModel)
class AppSettingsAdmin(ModelAdmin):
    list_display = ["user", "dark_mode", "parental_control", "notifications"]
    list_filter = ["dark_mode", "parental_control", "notifications"]
    search_fields = ["user__email", "user__username"]
