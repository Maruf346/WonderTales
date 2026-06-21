from django.urls import path
from .views import AppSettingsView

urlpatterns = [
    path('app-settings', AppSettingsView.as_view(), name='app-settings'),
]