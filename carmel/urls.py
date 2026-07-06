from . import views
from django.urls import path

urlpatterns = [
    path("", views.carmel_profile, name="carmel_profile"),
    path("edit/", views.edit_carmel, name="edit_carmel"),
]
