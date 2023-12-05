from django.urls import path
from mainapp.views import workstatus_review

patterns = [
    path('workstatus/', workstatus_review.workstatus_review, name='workstatus'),
]