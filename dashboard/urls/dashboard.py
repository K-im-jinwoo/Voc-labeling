from django.urls import path
from .. import views as dashboard_views

app_name = "dashboard"

urlpatterns = [
    path("", dashboard_views.dashboard ,name="dashboard"),
]
