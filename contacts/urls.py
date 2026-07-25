from django.urls import path

from . import views

app_name = "contacts"

urlpatterns = [
    path("<slug:member_slug>/info", views.contacts, name="index"),
    # PHONE
    path(
        "<slug:member_slug>/phones/create/",
        views.register_phone,
        name="register_phone",
    ),
    path(
        "phones/<int:id>/delete/",
        views.delete_phone,
        name="delete_phone",
    ),
    # ADDRESS
    path(
        "<slug:member_slug>/address/create/",
        views.register_address,
        name="register_address",
    ),
    path(
        "<slug:member_slug>/address/update/",
        views.edit_address,
        name="edit_address",
    ),
    path(
        "<slug:member_slug>/address/delete/",
        views.delete_address,
        name="delete_address",
    ),
]
