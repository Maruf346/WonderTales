from django.db import models
from django.conf import settings

# Create your models here.
class AppDetailsModel(models.Model):
    class Meta:
        app_label = 'admins'
        db_table = 'App Details Table'

    # default fields
    terms_and_conditions = models.TextField(blank=True, null=True)
    privacy_policy = models.TextField(blank=True, null=True)
    about_us = models.TextField(blank=True, null=True)
    contact_us = models.TextField(blank=True, null=True)

    def __str__(self):
        return "App Details"

class ReportModel(models.Model):
    TARGET_TYPE_CHOICES = [
        ('recipe', 'Recipe'),
        ('comment', 'Comment'),
        ('user', 'User'),
    ]

    class Meta:
        verbose_name = "Report"
        verbose_name_plural = "Reports"
        app_label = 'admins'
        db_table = 'Reports Table'

    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports_made')
    target_id = models.CharField(max_length=255)
    target_type = models.CharField(max_length=20, choices=TARGET_TYPE_CHOICES)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report by {self.reporter} on {self.target_type} {self.target_id} "

class PricingPlanModel(models.Model):
    class Meta:
        verbose_name = "Pricing Plan"
        verbose_name_plural = "Pricing Plans"
        app_label = 'admins'
        db_table = 'Pricing Plans Table'

    name = models.CharField(max_length=100)
    price_per_month = models.DecimalField(max_digits=10, decimal_places=2)
    details = models.TextField()
    benefits = models.TextField(help_text="Bullet‑point description of what the plan includes, e.g. '3 AI stories, Save & replay...'")
    # Legacy field kept for backward compatibility (will not be exposed)
    points_included = models.IntegerField(default=0, editable=False)

    def __str__(self):
        return f"{self.name} - ${self.price_per_month}/mo"
