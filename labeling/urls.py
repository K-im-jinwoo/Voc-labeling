from django.urls import path
from .views import labeling_work as views_labeling_work, labeling_dummy as views_labeling_dummy

app_name = "labeling"

urlpatterns = [
    path(r"work/", views_labeling_work.labeling_work, name="work"),
    path("work/delete_label", views_labeling_work.delete_label, name="delete_label"),
    path("work/reset", views_labeling_work.reset, name="reset"),
    path("dummy/", views_labeling_dummy.dummy, name="dummy"),
]
