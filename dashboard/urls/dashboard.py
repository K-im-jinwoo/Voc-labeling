from django.urls import path
from dashboard.views import dashboard
from django.contrib.auth.views import LoginView, LogoutView
from .. import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard ,name="dashboard"),
    # path("dashboard_check/", dashboard_check ,name="dashboard_check")
]
