from django.urls import path
from . import views

app_name = "output"

urlpatterns = [
    path("", views.output, name="output"),
]
