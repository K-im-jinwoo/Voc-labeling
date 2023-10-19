from django.urls import path, include
from django.views.generic import TemplateView

from mainapp.urls import account, workstatus_review, workstatus_worker, assignment
from mainapp.views.workstatus_worker import server
from mainapp.views.account import main_page

app_name = "mainapp"

urlpatterns = [
    path("", main_page, name="main"),
    path("server/", server, name="server"),
]


urlpatterns += account.patterns
urlpatterns += workstatus_review.patterns
urlpatterns += workstatus_worker.patterns
urlpatterns += assignment.patterns
