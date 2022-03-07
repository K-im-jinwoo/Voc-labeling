from django.shortcuts import render

# Create your views here.

def output(request):
    return render(request, 'outputapp/output.html')