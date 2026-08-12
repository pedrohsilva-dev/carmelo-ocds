from django.urls import path
from . import views

urlpatterns = [
    path(
        "relatorio-financeiro/",
        views.financial_report,
        name="financial_report",
    ),
    path(
        "<slug:user>/register/",
        views.register_contribution,
        name="register_contribution",
    ),
    path(
        "listagem/<slug:slug>/", views.contribution_member, name="contribution_member"
    ),
    path(
        "edit/<slug:user>/pk/<int:id>",
        views.edit_contribution,
        name="edit_contribution",
    ),
    path(
        "update/<slug:user>/pk/<int:id>",
        views.update_contribution,
        name="update_contribution",
    ),
    path(
        "delete/<slug:user>/pk/<int:id>",
        views.delete_contribution,
        name="delete_contribution",
    ),
]
