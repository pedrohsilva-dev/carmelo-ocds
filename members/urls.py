from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.members_aLL, name="list_member"),
    path("informacoes/<slug:slug>", views.show_member, name="show_member"),
    # Members
    path("cadastrar/", views.register_member, name="register_member"),
    path("editar/<int:id>", views.update_member, name="update_member"),
    path("delete/<int:id>", views.delete_member, name="delete_member"),
    # ASSOCIATIONS
    path("votos/", include("votes.urls")),
    path("contribuicoes/", include("contributions.urls")),
    # HTMX
    path("filter_members/", views.filter_members, name="list_filter_members"),
]
