from django.urls import path
from labeling.views import labeling_dummy

patterns = [
    path("dummy/", labeling_dummy.dummy, name="dummy"),
]
