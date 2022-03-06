from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

def labeling_work(request):
    return render(request, 'labelingapp/labeling_work.html')

def labeling_inspect(request):
    return render(request, 'labelingapp/labeling_inspect.html')
