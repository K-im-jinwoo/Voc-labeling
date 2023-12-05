from django.urls import path

from .urls import (
    account as urls_account, 
    assignment as urls_assignment,
    workstatus_review as urls_workstatus_review, 
    workstatus_worker as urls_workstatus_worker, 
    )
from .views import (
    workstatus_worker as views_workstatus_worker, 
    account as views_account,
    )


app_name = "main"

urlpatterns = [
    path("", views_account.main_page, name="main"),
    path("server/", views_workstatus_worker.server, name="server"),
]

urlpatterns += urls_account.patterns
urlpatterns += urls_workstatus_review.patterns
urlpatterns += urls_workstatus_worker.patterns
urlpatterns += urls_assignment.patterns
