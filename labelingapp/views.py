from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

def labeling_work(request):
    return HttpResponse('작업')

def labeling_inspect(request):
    return HttpResponse('검수')
