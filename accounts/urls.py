from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("profile/", views.profile, name="profile"),
    path("register_phone/", views.register_phone, name="register_phone"),
    path("delete_phone/<int:id>", views.delete_phone, name="delete_phone"),
    path("register_address/", views.register_address, name="register_address"),
    path("edit_address/", views.edit_address, name="edit_address"),
    path("delete_address/", views.delete_address, name="delete_address"),
    path("forgot_password/", views.forgot_password, name="forgot_password"),
    path("reset_password/<str:token>/", views.reset_password, name="reset_password"),
]
