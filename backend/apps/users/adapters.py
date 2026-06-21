from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from apps.users.models import CustomUserModel

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Check if we should auto-verify the email for social login.
        """
        user = sociallogin.user
        if not user.id:
            # New user
            user.is_email_verified = True
        return super().pre_social_login(request, sociallogin)

    def save_user(self, request, sociallogin, form=None):
        """
        This is called when a new user is created via social login.
        """
        user = super().save_user(request, sociallogin, form)
        user.is_email_verified = True
        user.save()
        return user
