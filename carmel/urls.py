from . import views
from django.urls import path

urlpatterns = [
    path("", views.carmel_profile, name="carmel_profile"),
    path("novo/", views.create_carmel, name="create_carmel"),
    path("edit/", views.edit_carmel, name="edit_carmel"),
]
