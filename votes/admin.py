from django.contrib import admin

from votes.models import Vote, VotesRegistration

# Register your models here.


admin.site.register(Vote)
admin.site.register(VotesRegistration)
