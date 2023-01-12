from django.urls import path
from django.views.generic import TemplateView

from mainapp.views import assignment
from mainapp.views.assign_delete import assign_delete

patterns = [
    path('assignment/', assignment.assignment, name='assignment'),
]
