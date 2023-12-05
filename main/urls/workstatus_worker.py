from django.urls import path

from ..views import workstatus_worker as views_workstatus_worker

patterns = [
    path('workstatus/count/', views_workstatus_worker.workstatus_worker, name='workstatus_count'),
]