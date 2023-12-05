from django.urls import path
from . import views

app_name = "upload"

urlpatterns = [
    path("", views.upload_main, name="upload"),
    path("delete-category/", views.delete_category, name="delete"),
]
