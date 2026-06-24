from django.contrib import admin

# from contributions.models import Contribution
# from votes.models import Vote

from .models import Member, Phone, Address

# # =========================
# # INLINES (ESTILO UNFOLD)
# # =========================

# class VotesInline(admin.TabularInline):
#     model = Vote
#     extra = 0


# class ContributionInline(admin.TabularInline):
#     model = Contribution
#     extra = 0


# class PhoneInline(admin.TabularInline):
#     model = Phone
#     extra = 0

# # =========================
# # MEMBER ADMIN
# # =========================

# @admin.register(Member)
# class MemberAdmin(admin.ModelAdmin):

#     list_display = (
#         "email",
#         "name",
#         "roles",
#         "is_active",
#     )

#     search_fields = (
#         "email",
#         "name",
#     )

#     list_filter = (
#         "roles",
#         "is_active",
#     )

#     ordering = ("name",)

#     inlines = [
#         VotesInline,
#         ContributionInline,
#         PhoneInline
#     ]

#     fieldsets = (
#         ("Informações", {
#             "fields": (
#                 "email",
#                 "password",
#                 "name",
#                 "church",
#                 "entry_date",
#                 "carmel",
#                 "roles",
#                 "slug",
#                 'address'
#             )
#         }),

#         ("Permissões", {
#             "fields": (
#                 "is_active",
#                 "is_staff",
#                 "is_superuser",
#             )
#         }),
#     )

admin.site.register(Member)
admin.site.register(Address)
admin.site.register(Phone)
