from django.contrib import admin

from votes.models import Vote, VotesRegistration


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("member", "votes_registration", "type", "date", "year_duration")
    list_filter = ("type", "date")
    search_fields = ("member__name", "member__email", "votes_registration__name")
    autocomplete_fields = ("member", "votes_registration")
    ordering = ("-date",)


@admin.register(VotesRegistration)
class VotesRegistrationAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name", "description")
    ordering = ("name",)
