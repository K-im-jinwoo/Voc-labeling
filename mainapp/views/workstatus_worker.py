from django.urls import path

from mainapp import viewss

patterns = [
    path('workstatus/count/', viewss.workstatus_worker, name='workstatus_count')
]