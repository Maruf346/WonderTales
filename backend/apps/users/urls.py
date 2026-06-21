from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.profile import *
from .views.registration import *
from .views.auth import PasswordResetConfirmHTMLView, ManualPasswordResetConfirmView, DeleteAccountView
from .views.social_auth import GoogleLogin, AppleLogin
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'profiles', CustomUserViewSet)
router.register(r'children', ChildrenProfileViewSet, basename='children-profile')

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),

    # Signup & Verification Routes
    path('signup/', SignupView.as_view(), name='signup'),
    path('signup/verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('signup/resend-otp/', ResendOTPView.as_view(), name='resend-otp'),

    # Auth & JWT Routes
    path('auth/', include('dj_rest_auth.urls')),
    path('refresh-token/', TokenRefreshView.as_view(), name='token_refresh'), 

    # Password Reset Confirm (HTML & Manual)
    path(
        'auth/password/reset/confirm/<uidb64>/<token>/',
        PasswordResetConfirmHTMLView.as_view(),
        name='password_reset_confirm'
    ),
    path('auth/password/reset/confirm/manual/', ManualPasswordResetConfirmView.as_view(), name='manual-password-reset-confirm'),

    # Social Login Routes
    path('auth/google/', GoogleLogin.as_view(), name='google_login'),
    path('auth/apple/', AppleLogin.as_view(), name='apple_login'),   

    # Delete Account Route
    path('auth/delete-account/', DeleteAccountView.as_view(), name='delete-account'),
]
