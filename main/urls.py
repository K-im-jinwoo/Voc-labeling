from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from .views import (
    account as views_account,
    assignment as views_assignment,
    main_page as views_main_page,
    workstatus_review as views_workstatus_review,
    workstatus_worker as views_workstatus_worker, 
    )

app_name = "main"

urlpatterns = [
    path("", views_main_page.main_page, name="main"),
    # path("server/", views_workstatus_worker.server, name="server"),
    path("login/", LoginView.as_view(template_name="main/login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),

    path('info/', views_account.information, name='info'),
    path("signup/", views_account.AccountCreateView.as_view(), name="signup"),
    path("account/<int:pk>", views_account.AccountDetailView.as_view(), name="account"),
    path("update/<int:pk>", views_account.AccountUpdateView.as_view(), name="update"),
    path("delete/<int:pk>", views_account.AccountDeleteView.as_view(), name="delete"),
    path("account_profile/", views_account.ProfileCreateView.as_view(), name="account_profile"),
    path("update_profile/<int:pk>", views_account.ProfileUpdateView.as_view(), name="update_profile"),
    path("admin_secret_key/", views_account.admin_secret_key, name="admin_secret_key"),

    path('assignment/', views_assignment.assignment, name='assignment'),

    path('workstatus/', views_workstatus_review.workstatus_review, name='workstatus_review'),
    
    path('workstatus/worker/', views_workstatus_worker.workstatus_worker, name='workstatus_worker'),
]
