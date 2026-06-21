from rest_framework import serializers
from .models import CustomUserModel, ChildrenProfileModel
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from dj_rest_auth.serializers import JWTSerializer
from apps.admins.models import PricingPlanModel

# Create your serializers here.
class ChildrenProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChildrenProfileModel
        fields = [
            'id', 'user', 'child_name', 'child_image', 'child_age', 
            'child_gender', 'favourite_themes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

class PricingPlanBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = PricingPlanModel
        fields = ['id', 'name', 'price_per_month', 'details', 'benefits']

class CustomUserModelSerializer(serializers.ModelSerializer):
    children_profiles = ChildrenProfileSerializer(many=True, read_only=True)
    pricing_plan = PricingPlanBriefSerializer(read_only=True)

    class Meta:
        model = CustomUserModel
        fields = [
            'id', 'email', 'username',
            'date_of_birth', 'user_image', 'is_email_verified', 'is_active',
            'pricing_plan', 'children_profiles'
        ]
        read_only_fields = ['id', 'email', 'is_staff', 'is_superuser', 'is_active', 'is_email_verified']

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUserModel
        fields = ['email', 'password', 'date_of_birth']

    def create(self, validated_data):
        # Use the manager you already wrote to hash the password properly
        return CustomUserModel.objects.create_user(**validated_data)

class OtpVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6, min_length=6)

class ResendOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ProfileCompletionSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)

    class Meta:
        model = CustomUserModel
        fields = ['email', 'username', 'date_of_birth']
        extra_kwargs = {
            'username': {'required': True},
            'date_of_birth': {'required': True},
        }


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add custom fields to the response for Flutter
        data['username'] = self.user.username
        data['is_active'] = self.user.is_active
        data['pricing_plan'] = None
        if self.user.pricing_plan:
            data['pricing_plan'] = {
                'id': self.user.pricing_plan.id,
                'name': self.user.pricing_plan.name,
                'price_per_month': str(self.user.pricing_plan.price_per_month),
                'details': self.user.pricing_plan.details,
                'benefits': self.user.pricing_plan.benefits,
            }
        
        return data


from dj_rest_auth.serializers import PasswordResetSerializer
from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm as DjangoPasswordResetForm

class CustomPasswordResetSerializer(PasswordResetSerializer):
    password_reset_form_class = DjangoPasswordResetForm

    def save(self):
        request = self.context.get('request')
        opts = {
            'use_https': request.is_secure() if request else True,
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
            'request': request,
            'domain_override': request.get_host() if request else None,
            'email_template_name': 'registration/password_reset_email.txt',
            'html_email_template_name': 'registration/password_reset_email.html',
            'subject_template_name': 'registration/password_reset_subject.txt',
        }
        self.reset_form.save(**opts)
