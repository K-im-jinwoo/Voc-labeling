from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.urls import reverse

from mainapp.models import Category


def labeling_work(request):
    try:

        # category_product 변수를 get 방식 으로 받으면 세션에 저장
        if request.method == "GET":
            if 'category_product' in request.GET:
                category_product = request.GET['category_product']
                category_detail = Category.objects.filter(category_product=category_product)
                context = {'category_detail': category_detail}
                return render(request, 'labelingapp/labeling_work.html', context)

            else:
                category_product = request.GET['category_product']
                category_detail = Category.objects.filter(category_product=category_product)
                context = {'category_detail': category_detail}
                return render(request, 'labelingapp/labeling_work.html', context)






    # 예외처리
    except Exception as identifier:
        print(identifier)

    return render(request, 'labelingapp/labeling_work.html')


def labeling_inspect(request):
    return render(request, 'labelingapp/labeling_inspect.html')