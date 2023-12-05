from django.urls import path
from labelingapp.views import labeling_work

patterns = [
    path(r'work/', labeling_work.labeling_work, name='work'),
    path('work/delete_label', labeling_work.delete_label, name='delete_label'),
    path('work/reset', labeling_work.reset, name='reset'),
]