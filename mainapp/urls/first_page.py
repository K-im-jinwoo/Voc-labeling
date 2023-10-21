from django.urls import path
from mainapp.views import workstatus_worker
from mainapp.views import first_page
from mainapp.views import test

urlpatterns = [
    path("", test, name="test"),
]
