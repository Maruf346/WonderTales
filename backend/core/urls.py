from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect


#--------------------------------------
# DRF-YASG API Documentation
#--------------------------------------
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="wondertales API",
        default_version='v1',
        description="API documentation for wondertales",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
#--------------------------------------



#--------------------------------------
# Sentry Error Trigger
#--------------------------------------
def trigger_error(request):
    division_by_zero = 1 / 0
#--------------------------------------



#--------------------------------------
# Redirect backend root to docs
#--------------------------------------
def redirect_to_docs(request):
    """Redirect root URL to API documentation"""
    return redirect('schema-swagger-ui')
#--------------------------------------



#--------------------------------------
# Redirect admin root to custom user model list view
#--------------------------------------
def redirect_admin_index(request):
    """Redirect admin index and sidebar logo links directly to the Custom User list page"""
    if not request.user.is_authenticated:
        return redirect('/admin/login/?next=/admin/users/customusermodel/')
    return redirect('/admin/users/customusermodel/')
#--------------------------------------



from apps.users.views.social_auth import FlutterGoogleLoginView, FlutterAppleLoginView

urlpatterns = [
    path('admin/', redirect_admin_index),
    path('admin/', admin.site.urls),

    # Sentry Error Trigger
    path('sentry-debug/', trigger_error),

    # Flutter Custom Social Login Endpoints
    path('v1/user/google/id-token/', FlutterGoogleLoginView.as_view(), name='custom_google_login'),
    path('v1/dj-rest-auth/apple/', FlutterAppleLoginView.as_view(), name='custom_apple_login'),

    # Local app routes (v1 prefix)
    
    path('v1/users/', include('apps.users.urls')),
    
    path('v1/admins/', include('apps.admins.urls')),
    

    path('v1/app_settings/', include('apps.app_settings.urls')),

    path('v1/stories/', include('apps.story.urls')),
    path('v1/', include('apps.blogs.urls')),
    
    
    # API Documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),

    # Redirect root to docs
    path('', redirect_to_docs, name='root-redirect'),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)