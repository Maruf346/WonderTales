from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import BlogModel
from .serializers import BlogListSerializer, BlogDetailSerializer

class BlogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoints that allow blogs to be read.
    Lists only key summary fields, retrieves full detail by slug.
    """
    queryset = BlogModel.objects.all()
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BlogDetailSerializer
        return BlogListSerializer
