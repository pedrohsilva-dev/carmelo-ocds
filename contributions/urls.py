from django.urls import path
from . import views

urlpatterns = [
    path(
        "<slug:user>/register/",
        views.register_contribution,
        name="register_contribution",
    ),
    path(
        "listagem/<slug:slug>/", views.contribution_member, name="contribution_member"
    ),
    path(
        "delete/<slug:user>/pk/<int:id>",
        views.delete_contribution,
        name="delete_contribution",
    ),
]
