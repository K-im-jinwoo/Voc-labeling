from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.urls import reverse

from mainapp.models import Category, Review


def print_review(start, end, category_product):
    print_review_list = Review.objects.filter(category_product=category_product, review_number__range=(int(start), int(end)), first_status=False, second_status=False, dummy_status=False).order_by('review_number')[:1]
    return print_review_list


def labeling_work(request):
    try:

        # GET 방식의 request 처리
        if request.method == "GET":

            # 세 가지 변수를 모두 받아야 함.
            if 'category_product' in request.GET and 'start' in request.GET and 'end' in request.GET:

                # 청소기, 냉장고, 식기세척기 제품군 선택 시에만 수행
                if request.GET['category_product'] in ['cleaner', 'refrigerator', 'dish_washer']:
                    category_product = request.GET['category_product']
                    start = request.GET['start']
                    end = request.GET['end']

                    # 해당 제품군의 카테고리 정보 불러옴
                    category_detail = Category.objects.filter(category_product=category_product)

                    # 해당 제품군과 범위 중 제일 처음 한 개만 가져옴 => print_review() 함수 사용
                    review_first = print_review(start, end, category_product)

                    context = {'category_detail': category_detail, 'category_product': category_product,
                               'review_first': review_first}
                    return render(request, 'labelingapp/labeling_work.html', context)

            else:
                context = {'message': '제품, 범위를 다시 선택해주세요.'}
                return render(request, 'labelingapp/labeling_work.html', context)




    # 예외처리
    except Exception as identifier:
        print(identifier)

    return render(request, 'labelingapp/labeling_work.html')


def labeling_inspect(request):
    return render(request, 'labelingapp/labeling_inspect.html')