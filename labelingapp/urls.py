from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from . import views

app_name = 'labelingapp'

urlpatterns = [
    
    path('work/', views.labeling_work, name='work'),
#     path(r'work/', views.labeling_work, name='work'),
    path('work/delete_label', views.delete_label, name='delete_label'),
    path('work/reset', views.reset, name='reset'),
    path(r'inspect/', views.labeling_inspect, name='inspect'),
    path('inspect/delete_label', views.delete_label, name='delete_label'),
    path('inspect/delete_inspect_label', views.delete_inspect_label, name='delete_inspect_label'),
    path('inspect/inspect_reset', views.inspect_reset, name='inspect_reset'),



]
