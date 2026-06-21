from rest_framework import generics, status, permissions
from rest_framework.response import Response
from .models import AppDetailsModel, ReportModel
from .serializers import AppDetailsSerializer, ReportSerializer

# Create your views here.
class AppDetailsView(generics.RetrieveUpdateAPIView):
    serializer_class = AppDetailsSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'head', 'options']

    def get_object(self):
        # Automatically get or create the singleton instance
        return AppDetailsModel.objects.first()

    def post(self, request, *args, **kwargs):
        if AppDetailsModel.objects.exists():
            return Response(
                {"detail": "App details already exist. Use PATCH to update."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response({"detail": "App details not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class ReportCreateView(generics.CreateAPIView):
    queryset = ReportModel.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)

class PricingPlanListView(generics.ListAPIView):
    """Returns all 3 pricing plans. Public endpoint — no auth required."""
    from .models import PricingPlanModel
    from .serializers import PricingPlanSerializer
    queryset = PricingPlanModel.objects.all()
    serializer_class = PricingPlanSerializer
    permission_classes = [permissions.AllowAny]
