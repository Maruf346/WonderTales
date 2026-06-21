from django.db import models
from apps.users.models import CustomUserModel
# Create your models here.
class AppSettingsModel(models.Model):
    class Meta:
        verbose_name = "App Settings"
        verbose_name_plural = "App Settings"


    dark_mode = models.BooleanField(default=False)
    parental_control = models.BooleanField(default=False)
    comments = models.BooleanField(default=False)
    notifications = models.BooleanField(default=False)
    

    user = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - App Settings"
    
    
    
