from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'outputapp'

urlpatterns = [

    path('', views.output, name='output'),

]
