from django.urls import path
from . import views

urlpatterns = [
    # VOTES MEMBER
    path("list/<slug:slug>/", views.votes_member, name="votes_members"),
    path("register_vote/", views.register_vote, name="register_vote"),
    path("vote_member/<str:user>/pk/<int:id>", views.vote_member, name="vote_member"),
    path(
        "edit_vote_member/<str:user>/pk/<int:id>",
        views.edit_vote_member,
        name="edit_vote_member",
    ),
    path(
        "update_vote_member/<int:id>",
        views.update_vote_member,
        name="update_vote_member",
    ),
    path("delete_vote/<int:id>", views.delete_vote, name="delete_vote"),
    # REGISTER VOTES DEFAULT
    path("votes_registration/", views.votes_registration, name="votes_registration"),
    path(
        "register_votes_registration/",
        views.register_votes_registration,
        name="register_votes_registration",
    ),
    path(
        "edit_vote_registration/pk/<int:id>",
        views.edit_vote_registration,
        name="edit_vote_registration",
    ),
    path(
        "update_vote_registration/pk/<int:id>",
        views.update_vote_registration,
        name="update_vote_registration",
    ),
    path(
        "delete_votes_registration/pk/<int:id>",
        views.delete_votes_registration,
        name="delete_votes_registration",
    ),
]
