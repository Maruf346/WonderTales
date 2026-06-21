from django.urls import path
from .views import AppDetailsView, ReportCreateView, PricingPlanListView

urlpatterns = [
    # Add your routes here
    path('app-details/', AppDetailsView.as_view(), name='app-details'),
    path('pricing-plans/', PricingPlanListView.as_view(), name='pricing-plans'),
]
