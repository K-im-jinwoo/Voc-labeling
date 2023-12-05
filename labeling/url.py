from labeling.urls import labeling_dummy, labeling_work

app_name = "labeling"

urlpatterns = list()
urlpatterns += labeling_work.patterns
urlpatterns += labeling_dummy.patterns
