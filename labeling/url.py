from django.urls import path

from labelingapp.urls import dummy_to_trashcan, labeling_inspect, labeling_work

app_name = 'labelingapp'

urlpatterns = list()
urlpatterns += labeling_work.patterns
urlpatterns += labeling_inspect.patterns
urlpatterns += dummy_to_trashcan.patterns