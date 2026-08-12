from django.contrib import admin

from contributions.models import Contribution


@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ("member", "date_pay", "price", "carmel", "created_at")
    list_filter = ("date_pay", "carmel")
    search_fields = ("member__name", "member__email")
    autocomplete_fields = ("member", "carmel")
    ordering = ("-date_pay",)
    date_hierarchy = "date_pay"
