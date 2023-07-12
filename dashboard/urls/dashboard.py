from django.urls import path
from dashboard.views import dashboard
from django.contrib.auth.views import LoginView, LogoutView

app_name = "dashboard"

urlpatterns = [
    path("", dashboard, name="dashboard"),
    # path("dashboard_check/", dashboard_check ,name="dashboard_check")
]