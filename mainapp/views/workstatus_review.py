from django.urls import path

from mainapp import viewss

patterns = [
    path('workstatus/', viewss.workstatus_review, name='workstatus'),
]