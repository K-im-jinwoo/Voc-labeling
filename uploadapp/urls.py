
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from . import views

app_name = 'uploadapp'

urlpatterns = [
    path('', views.upload_main, name="upload")

]
