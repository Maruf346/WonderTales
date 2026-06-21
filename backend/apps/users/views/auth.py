from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from apps.users.models import CustomUserModel
from django.contrib.auth.tokens import default_token_generator
from rest_framework.permissions import AllowAny, IsAuthenticated

class PasswordResetConfirmHTMLView(TemplateView):
    template_name = 'registration/password_reset_confirm.html'

class ManualPasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        uidb64 = request.data.get('uid')
        token = request.data.get('token')
        password = request.data.get('new_password1')
        password_confirm = request.data.get('new_password2')

        if not all([uidb64, token, password, password_confirm]):
            return Response({"detail": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

        if password != password_confirm:
            return Response({"new_password1": ["Passwords do not match."]}, status=status.HTTP_400_BAD_REQUEST)

        if len(password) < 8:
            return Response({"new_password1": ["Password must be at least 8 characters long."]}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUserModel.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUserModel.DoesNotExist):
            return Response({"uid": ["Invalid value"]}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"token": ["Invalid or expired token."]}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(password)
        user.save()
        
        return Response({"detail": "Password has been reset successfully."}, status=status.HTTP_200_OK)

class DeleteAccountView(APIView):
    """
    Delete the currently authenticated user's account.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user
        user.delete()
        return Response({"detail": "Account deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
