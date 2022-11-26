from django.urls import path, include
from django.views.generic import TemplateView

from mainapp.urls import account, workstatus_review, workstatus_worker

app_name = 'mainapp'

urlpatterns = [
    path('', TemplateView.as_view(template_name="mainapp/main_page.html"), name='main'),
]

urlpatterns += account.patterns
urlpatterns += workstatus_review.patterns
urlpatterns += workstatus_worker.patterns
