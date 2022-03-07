from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

app_name = 'mainapp'

urlpatterns = [

    path('', TemplateView.as_view(template_name="mainapp/main_page.html"), name='main'),

]
