from django.urls import path
from django.views.generic import TemplateView

from mainapp.views import assignment

patterns = [
    path('assignment/', assignment.assignment, name='assignment'),
]
