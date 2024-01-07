from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("date", views.dashboard_by_date, name="dashboard_date")
]
