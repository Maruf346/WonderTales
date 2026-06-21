from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import CustomUserModel
from django.db.models import Count
from django.db.models.functions import TruncDay
from django.utils import timezone
from datetime import timedelta
import json

@admin.register(CustomUserModel)
class UserAdmin(ModelAdmin):
    list_display = ["email", "username", "is_paid", "is_active", "is_email_verified", "date_joined"]
    list_filter = ["is_paid", "is_active", "is_email_verified", "is_staff"]
    search_fields = ["email", "username"]
    inlines = []
    
    def changelist_view(self, request, extra_context=None):
        """Override to add custom statistics and ChartJS data for admin dashboard visualization"""
        extra_context = extra_context or {}
        
        # Calculate standard user metrics
        total_users = CustomUserModel.objects.count()
        active_users = CustomUserModel.objects.filter(is_active=True).count()
        paid_users = CustomUserModel.objects.filter(is_paid=True).count()
        unpaid_users = CustomUserModel.objects.filter(is_paid=False).count()
        
        extra_context.update({
            "total_users": total_users,
            "active_users": active_users,
            "paid_users": paid_users,
            "unpaid_users": unpaid_users,
        })
        
        # 1. New Registrations Interval Chart Logic
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        weekly_start = now - timedelta(days=7)
        monthly_start = now - timedelta(days=30)
        
        today_new = CustomUserModel.objects.filter(date_joined__gte=today_start).count()
        weekly_new = CustomUserModel.objects.filter(date_joined__gte=weekly_start).count()
        monthly_new = CustomUserModel.objects.filter(date_joined__gte=monthly_start).count()
        
        reg_chart_data = {
            "labels": ["Today's New", "Weekly New (7d)", "Monthly New (30d)"],
            "datasets": [{
                "label": "Registrations",
                "data": [today_new, weekly_new, monthly_new],
                "backgroundColor": [
                    "rgba(99, 102, 241, 0.75)", # Indigo
                    "rgba(139, 92, 246, 0.75)", # Purple
                    "rgba(236, 72, 153, 0.75)"  # Pink
                ],
                "borderColor": [
                    "#4f46e5",
                    "#7c3aed",
                    "#ec4899"
                ],
                "borderWidth": 1.5
            }]
        }
        extra_context["registration_chart"] = json.dumps(reg_chart_data)
        
        # 2. Total vs Paid Comparison Chart Logic (Last 7 Days Cumulative)
        dates = [now.date() - timedelta(days=i) for i in range(6, -1, -1)]
        labels = [d.strftime("%b %d") for d in dates]
        
        total_counts = []
        paid_counts = []
        
        for d in dates:
            end_of_day = timezone.make_aware(timezone.datetime.combine(d, timezone.datetime.max.time()))
            total_counts.append(CustomUserModel.objects.filter(date_joined__lte=end_of_day).count())
            paid_counts.append(CustomUserModel.objects.filter(date_joined__lte=end_of_day, is_paid=True).count())
            
        comp_chart_data = {
            "labels": labels,
            "datasets": [
                {
                    "label": "Total Users",
                    "data": total_counts,
                    "borderColor": "#6366f1",
                    "backgroundColor": "rgba(99, 102, 241, 0.05)",
                    "tension": 0.4,
                    "fill": True
                },
                {
                    "label": "Paid Users",
                    "data": paid_counts,
                    "borderColor": "#f59e0b",
                    "backgroundColor": "rgba(245, 158, 11, 0.05)",
                    "tension": 0.4,
                    "fill": True
                }
            ]
        }
        extra_context["comparison_chart"] = json.dumps(comp_chart_data)
        
        return super().changelist_view(request, extra_context=extra_context)

# Unfold Dashboard Stats
def user_stats_callback(request, context):
    context.update({
        "total_users": CustomUserModel.objects.count(),
        "active_users": CustomUserModel.objects.filter(is_active=True).count(),
        "paid_users": CustomUserModel.objects.filter(is_paid=True).count(),
    })

    try:
        data = (
            CustomUserModel.objects
            .annotate(date=TruncDay("date_joined"))
            .values("date")
            .annotate(count=Count("id"))
            .order_by("date")
        )

        labels = [d["date"].strftime("%Y-%m-%d") for d in data] if data else []
        values = [d["count"] for d in data] if data else []
        
        chart_data = {
            "labels": labels,
            "datasets": [{
                "label": "New Users",
                "data": values,
                "borderColor": "#7c3aed", 
                "backgroundColor": "rgba(124, 58, 237, 0.1)",
                "tension": 0.4,
                "fill": True
            }],
        }
        context["dashboard_chart"] = json.dumps(chart_data)
    except Exception as e:
        context["dashboard_chart"] = json.dumps({"labels": [], "datasets": []})

    return context