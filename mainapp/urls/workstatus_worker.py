from django.urls import path
from mainapp.views import workstatus_worker

patterns = [
    path('workstatus/count/', workstatus_worker.workstatus_worker, name='workstatus_count')
]