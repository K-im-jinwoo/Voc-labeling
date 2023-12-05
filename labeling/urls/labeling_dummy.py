from django.urls import path
from labelingapp.views import dummy_to_trashcan

patterns = [
    path('dummydummy/', dummy_to_trashcan.dummydummy, name='dummydummy'),
]