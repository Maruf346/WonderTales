from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, parsers
from ..models import CustomUserModel, ChildrenProfileModel
from ..serializers import CustomUserModelSerializer, ChildrenProfileSerializer
from rest_framework.permissions import IsAuthenticated

class CustomUserViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = CustomUserModel.objects.all()
    serializer_class = CustomUserModelSerializer

    @action(detail=False, methods=['get', 'patch'], parser_classes=[parsers.MultiPartParser, parsers.FormParser])
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        elif request.method == 'PATCH':
            serializer = self.get_serializer(request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChildrenProfileViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ChildrenProfileSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_queryset(self):
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False) or self.request.user.is_anonymous:
            return ChildrenProfileModel.objects.none()
            
        # Only return profiles belonging to the authenticated user
        return ChildrenProfileModel.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Set the user to the current authenticated user
        serializer.save(user=self.request.user)