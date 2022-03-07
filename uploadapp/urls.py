from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'uploadapp'

urlpatterns = [

    path('', views.upload, name='upload'),

]
