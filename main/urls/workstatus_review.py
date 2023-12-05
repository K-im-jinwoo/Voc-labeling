from django.urls import path

from ..views import workstatus_review as views_workstatus_review

patterns = [
    path('workstatus/', views_workstatus_review.workstatus_review, name='workstatus'),
]