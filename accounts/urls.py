from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.register, name="register"),
    path("register/", views.register),
    path("login/", views.PWDigitalLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("dashboard/", login_required(views.dashboard_redirect), name="dashboard_redirect"),
    path("profile/", login_required(views.profile), name="profile"),
]
