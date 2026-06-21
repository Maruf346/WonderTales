from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import AppDetailsModel, ReportModel

@admin.register(AppDetailsModel)
class AppDetailsAdmin(ModelAdmin):
    list_display = ["__str__"]
    
@admin.register(ReportModel)
class ReportAdmin(ModelAdmin):
    list_display = ["reporter", "target_type", "target_id", "created_at"]
    list_filter = ["target_type", "created_at"]
    search_fields = ["reporter__email", "target_id", "reason"]

from .models import PricingPlanModel

@admin.register(PricingPlanModel)
class PricingPlanAdmin(ModelAdmin):
    list_display = ["name", "price_per_month", "benefits"]
    
    def has_add_permission(self, request):
        # Admin cannot add new plans, only edit existing ones
        return False
        
    def has_delete_permission(self, request, obj=None):
        # Admin cannot delete plans
        return False