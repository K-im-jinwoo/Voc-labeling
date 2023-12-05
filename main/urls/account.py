from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from ..views import account as views_account

patterns = [
    path('info/', views_account.information, name='info'),
    path("login/", LoginView.as_view(template_name="main/login.html"), name="login"),
    path("signup/", views_account.AccountCreateView.as_view(), name="signup"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("account/<int:pk>", views_account.AccountDetailView.as_view(), name="account"),
    path("update/<int:pk>", views_account.AccountUpdateView.as_view(), name="update"),
    path("delete/<int:pk>", views_account.AccountDeleteView.as_view(), name="delete"),
    path("account_profile/", views_account.ProfileCreateView.as_view(), name="account_profile"),
    path("update_profile/<int:pk>", views_account.ProfileUpdateView.as_view(), name="update_profile"),
    path("admin_secret_key/", views_account.admin_secret_key, name="admin_secret_key"),
]
