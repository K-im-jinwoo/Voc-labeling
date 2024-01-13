from django.urls import path
from .views import labeling_work as views_labeling_work

app_name = "labeling"

urlpatterns = [
    path(r"work/", views_labeling_work.labeling_work, name="work"),
]
