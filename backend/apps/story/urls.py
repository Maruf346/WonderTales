from rest_framework.routers import DefaultRouter
from .views import StoryModelViewSet, VoiceCloneViewSet

router = DefaultRouter()
router.register(r'stories', StoryModelViewSet, basename='story')
router.register(r'voices', VoiceCloneViewSet, basename='voiceclone')

urlpatterns = router.urls