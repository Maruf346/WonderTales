from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import AppSettingsModel
from .serializers import AppSettingsSerializer

class AppSettingsView(generics.RetrieveUpdateAPIView):
    """
    API view to retrieve and update the current user's app settings.
    No ID is required in the URL.
    """
    serializer_class = AppSettingsSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'patch', 'head', 'options']

    def get_object(self):
        # Automatically get or create the settings for the logged-in user
        obj, created = AppSettingsModel.objects.get_or_create(user=self.request.user)
        return obj
    