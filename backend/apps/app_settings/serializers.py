from rest_framework import serializers
from .models import AppSettingsModel

class AppSettingsSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = AppSettingsModel
        fields = '__all__'      