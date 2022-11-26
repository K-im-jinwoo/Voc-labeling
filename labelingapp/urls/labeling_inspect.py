from django.urls import path
from labelingapp.views import labeling_inspect

patterns = [
    path(r'inspect/', labeling_inspect.labeling_inspect, name='inspect'),
    path('inspect/delete_label', labeling_inspect.delete_label, name='delete_label'),
    path('inspect/delete_inspect_label', labeling_inspect.delete_inspect_label, name='delete_inspect_label'),
    path('inspect/inspect_reset', labeling_inspect.inspect_reset, name='inspect_reset'),
]