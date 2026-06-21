from rest_framework import serializers
from .models import BlogModel

class BlogListSerializer(serializers.ModelSerializer):
    tags_list = serializers.SerializerMethodField()

    class Meta:
        model = BlogModel
        fields = [
            'id',
            'title',
            'slug',
            'image',
            'updated_at',
            'tags_list',
        ]

    def get_tags_list(self, obj):
        if obj.tags:
            return [tag.strip() for tag in obj.tags.split(',') if tag.strip()]
        return []

class BlogDetailSerializer(serializers.ModelSerializer):
    tags_list = serializers.SerializerMethodField()

    class Meta:
        model = BlogModel
        fields = [
            'id',
            'title',
            'slug',
            'author',
            'content',
            'image',
            'tags_list',
            'created_at',
            'updated_at',
            'meta_title',
            'meta_description',
            'meta_keywords',
        ]

    def get_tags_list(self, obj):
        if obj.tags:
            return [tag.strip() for tag in obj.tags.split(',') if tag.strip()]
        return []
