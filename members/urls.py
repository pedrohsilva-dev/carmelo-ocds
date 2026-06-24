from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.members_aLL, name="list_member"),
    path("show/<slug:slug>", views.show_member, name="show_member"),
    # Members
    path("register/", views.register_member, name="register_member"),
    path("update/<int:id>", views.update_member, name="update_member"),
    path("delete/<int:id>", views.delete_member, name="delete_member"),
    # ASSOCIATIONS
    path("votes/", include("votes.urls")),
    path("contributions/", include("contributions.urls")),
    # HTMX
    path("filter_members/", views.filter_members, name="list_filter_members"),
]
