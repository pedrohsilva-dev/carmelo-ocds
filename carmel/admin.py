from django.contrib import admin

from carmel.models import Carmel


@admin.register(Carmel)
class CarmelAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "city",
        "diocese",
        "price_contribution_default",
        "pay_day_contribution_default",
        "created_at",
    )
    search_fields = ("name", "city", "diocese")
    ordering = ("name",)
