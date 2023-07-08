from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from mainapp.views.account import (
    AccountCreateView,
    AccountDetailView,
    ProfileCreateView,
    AccountUpdateView,
    AccountDeleteView,
    ProfileUpdateView,
    admin_secret_key,
)

patterns = [
    path("login/", LoginView.as_view(template_name="mainapp/login.html"), name="login"),
    path("signup/", AccountCreateView.as_view(), name="signup"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("account/<int:pk>", AccountDetailView.as_view(), name="account"),
    path("update/<int:pk>", AccountUpdateView.as_view(), name="update"),
    path("delete/<int:pk>", AccountDeleteView.as_view(), name="delete"),
    path("account_profile/", ProfileCreateView.as_view(), name="account_profile"),
    path("update_profile/<int:pk>", ProfileUpdateView.as_view(), name="update_profile"),
    path("admin_secret_key/", admin_secret_key, name="admin_secret_key"),
]
