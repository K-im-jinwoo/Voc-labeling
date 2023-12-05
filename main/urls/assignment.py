from django.urls import path

from ..views import assignment as views_assignment

patterns = [
    path('assignment/', views_assignment.assignment, name='assignment'),
]
