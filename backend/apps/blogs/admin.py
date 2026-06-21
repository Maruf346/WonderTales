from django.contrib import admin
from django.db import models
from unfold.admin import ModelAdmin
from unfold.contrib.forms.widgets import WysiwygWidget
from .models import BlogModel

@admin.register(BlogModel)
class BlogAdmin(ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'updated_at')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'content', 'tags')
    list_filter = ('created_at', 'updated_at')
    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        }
    }
