from django.contrib.auth.models import User
from django.shortcuts import render

from mainapp.models import Category, Review

from django.http import JsonResponse


def test(request):
    a = 2
    print(a)
    context = {"a": a}
    return render(request, "mainapp/first_page.html", context=context)
