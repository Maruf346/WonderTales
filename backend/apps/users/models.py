from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from apps.admins.models import PricingPlanModel

# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        # Assign Free plan if not provided
        if not user.pricing_plan_id:
            try:
                free_plan = PricingPlanModel.objects.get(name='Free')
                user.pricing_plan = free_plan
            except PricingPlanModel.DoesNotExist:
                pass
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)



class CustomUserModel(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = "User"           # Singular name
        verbose_name_plural = "Users Account"   # Plural name
        app_label = 'users'
        db_table = 'Users Table'


    # defauld fields
    email = models.EmailField(unique=True)
    username = models.TextField(max_length=15, unique=True, blank=True, null=True)


    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    # custom fields
    date_of_birth = models.DateField(blank=True, null=True)
    user_image = models.ImageField(upload_to='users/profile_pictures/', blank=True, null=True)
    is_paid = models.BooleanField(default=False, help_text="Designates whether this user has a paid subscription.")

    # Verification Trackers
    is_email_verified = models.BooleanField(default=False) 

    
    verification_code = models.CharField(max_length=6, blank=True, null=True)

    
    is_active = models.BooleanField(default=True)
    pricing_plan = models.ForeignKey('admins.PricingPlanModel', on_delete=models.SET_NULL, null=True, blank=True, related_name='subscribers')

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class ChildrenProfileModel(models.Model):
    """
    This model is used to store the profile information of the children.
    """
    class Meta:
        verbose_name = "Children Profile"           # Singular name
        verbose_name_plural = "Children Profile"   # Plural name
        app_label = 'users'
        db_table = 'Children Profile Table'

    # Relationships
    user = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE, related_name='children_profiles')

    # Default fields
    child_name = models.CharField(max_length=100, blank=True, null=True)
    child_image = models.ImageField(upload_to='children_images/', blank=True, null=True)
    child_age = models.IntegerField(blank=True, null=True)
    child_gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female')], blank=True, null=True)
    favourite_themes = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.child_name} - {self.user.email}"
    