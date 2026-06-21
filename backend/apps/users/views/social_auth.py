from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

class GoogleLogin(SocialLoginView):
    """
    Google Login API endpoint.
    Flutter developer should send the 'access_token' or 'id_token' received from Google.
    """
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://localhost:8000/auth/google/callback/" 
    client_class = OAuth2Client

class AppleLogin(SocialLoginView):
    """
    Apple Login API endpoint.
    Flutter developer should send the 'access_token' or 'id_token' received from Apple.
    """
    adapter_class = AppleOAuth2Adapter
    callback_url = "https://wonder-tales.com/auth/apple/callback/"
    client_class = OAuth2Client

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

CustomUserModel = get_user_model()

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


# ── Request Serializers for Swagger ──────────────────────────────────────────

class FlutterGoogleLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(help_text="Google account email address")

class FlutterAppleLoginSerializer(serializers.Serializer):
    id_token = serializers.CharField(help_text="Apple identity token from Flutter SDK (credential.identityToken)")
    email = serializers.EmailField(required=False, help_text="User email. Required on first login. Must be persisted by Flutter and re-sent on subsequent logins.")


# ── Shared response schema ────────────────────────────────────────────────────

_user_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id':            openapi.Schema(type=openapi.TYPE_INTEGER,  description="User database ID"),
        'email':         openapi.Schema(type=openapi.TYPE_STRING,   description="User email"),
        'full_name':     openapi.Schema(type=openapi.TYPE_STRING,   description="Display name"),
        'profile_image': openapi.Schema(type=openapi.TYPE_STRING,   description="Profile image URL"),
    }
)

_social_login_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Always true on success"),
        'created': openapi.Schema(type=openapi.TYPE_BOOLEAN, description="True if a new account was just created"),
        'refresh': openapi.Schema(type=openapi.TYPE_STRING,  description="Long-lived JWT refresh token"),
        'access':  openapi.Schema(type=openapi.TYPE_STRING,  description="Short-lived JWT access token"),
        'user':    _user_schema,
    }
)


# ── Views ─────────────────────────────────────────────────────────────────────

class FlutterGoogleLoginView(APIView):
    """
    Custom Google login — accepts the verified email from the Flutter Google Sign-In SDK.
    Returns JWT access + refresh tokens and basic user info.
    """
    permission_classes = []

    @swagger_auto_schema(
        operation_summary="Google Login (Flutter)",
        operation_description=(
            "Send the email obtained from Google Sign-In on Flutter. "
            "If no account exists for that email a new one is created automatically.\n\n"
            "**Flutter snippet:**\n"
            "```dart\n"
            "final googleAuth = await googleUser.authentication;\n"
            "// Send the user's email — NOT the id_token for this endpoint\n"
            "```"
        ),
        request_body=FlutterGoogleLoginSerializer,
        responses={
            200: openapi.Response("Login successful", _social_login_response),
            400: openapi.Response("Missing email"),
        },
        tags=["Social Auth"],
    )
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"success": False, "error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        user, created = CustomUserModel.objects.get_or_create(email=email)
        if created:
            user.set_unusable_password()
            user.is_email_verified = True
            user.username = email.split('@')[0]
            user.save()
            
        tokens = get_tokens_for_user(user)
        
        user_data = {
            "id": user.id,
            "email": user.email,
            "full_name": user.username or email.split('@')[0],
            "profile_image": request.build_absolute_uri(user.user_image.url) if user.user_image else "https://prommt.cc/profile_images/default_avatar.png",
            "pricing_plan": {
                "id": user.pricing_plan.id,
                "name": user.pricing_plan.name,
                "price_per_month": str(user.pricing_plan.price_per_month),
                "benefits": user.pricing_plan.benefits,
            } if user.pricing_plan else None
        }
        
        return Response({
            "success": True,
            "created": created,
            "refresh": tokens['refresh'],
            "access": tokens['access'],
            "user": user_data
        })


class FlutterAppleLoginView(APIView):
    """
    Custom Apple login — accepts the identity token and email from the Flutter Sign in with Apple SDK.
    Returns JWT access + refresh tokens and basic user info.
    """
    permission_classes = []

    @swagger_auto_schema(
        operation_summary="Apple Login (Flutter)",
        operation_description=(
            "Send the `identityToken` from Apple and the user's email.\n\n"
            "⚠️ **Apple Email Behaviour:** Apple only provides the email on the very first login. "
            "Your Flutter app must save it to SecureStorage and re-send it on every subsequent login.\n\n"
            "**Flutter snippet:**\n"
            "```dart\n"
            "final credential = await SignInWithApple.getAppleIDCredential(...);\n"
            "final idToken = credential.identityToken; // ← always present\n"
            "final email  = credential.email;          // ← null after first login, read from storage\n"
            "```"
        ),
        request_body=FlutterAppleLoginSerializer,
        responses={
            200: openapi.Response("Login successful", _social_login_response),
            400: openapi.Response("Missing id_token or email"),
        },
        tags=["Social Auth"],
    )
    def post(self, request):
        id_token = request.data.get('id_token')
        email = request.data.get('email')
        
        if not id_token:
            return Response({"success": False, "error": "id_token is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        if not email:
            return Response({"success": False, "error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        user, created = CustomUserModel.objects.get_or_create(email=email)
        if created:
            user.set_unusable_password()
            user.is_email_verified = True
            user.username = email.split('@')[0]
            user.save()
            
        tokens = get_tokens_for_user(user)
        
        user_data = {
            "id": user.id,
            "email": user.email,
            "full_name": user.username or email.split('@')[0],
            "profile_image": request.build_absolute_uri(user.user_image.url) if user.user_image else "https://prommt.cc/profile_images/default_avatar.png",
            "pricing_plan": {
                "id": user.pricing_plan.id,
                "name": user.pricing_plan.name,
                "price_per_month": str(user.pricing_plan.price_per_month),
                "benefits": user.pricing_plan.benefits,
            } if user.pricing_plan else None
        }
        
        return Response({
            "success": True,
            "created": created,
            "refresh": tokens['refresh'],
            "access": tokens['access'],
            "user": user_data
        })
