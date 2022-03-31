from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.urls import reverse, resolve

from mainapp.models import Category, Review, FirstLabeledData


# start~end 범위 내 처리 안된 데이터 보여줌
def print_review(start, end, category_product):
    print_review_list = Review.objects.filter(category_product=category_product,
                                              review_number__range=(int(start), int(end)),
                                              first_status=False, second_status=False, dummy_status=False).order_by(
        'review_number')[:1]
    return print_review_list


def labeling_work(request):
    try:

        # reqeust한 URL의 파라미터에 제품군, 시작위치, 끝 위치가 있으면 데이터를 반환함
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

                # labeling_work.html에 보낼 context 데이터
                context = {'category_detail': category_detail, 'category_product': category_product,
                           'review_first': review_first, 'start': start, 'end': end}

                # POST 방식 request 받았을 때 수행함.
                if request.method == "POST" and 'labeled_expression' in request.POST and 'labeled_target' in request.POST:

                    # 들어온 값 변수에 저장
                    target = request.POST.get('labeled_target')
                    emotion = request.POST.get('labeled_emotion')
                    expression = request.POST.get('labeled_expression')
                    review_id = request.POST.get('review_id')  # 해당 리뷰 id 받아오기
                    category_id = request.POST.get('category_id')  # 해당하는 리뷰에 맞는 카테고리id를 받아오기
                    print(target, emotion, expression)

                    # First_Labeled_Data모델을 불러와서 first_labeled_data에 저장
                    first_labeled_data = FirstLabeledData()

                    # laveling_work에서 불러온 값들을 first_labeled_data 안에 정해진 db이름으로 넣음
                    first_labeled_data.first_labeled_emotion = emotion  # 긍,부정 저장
                    first_labeled_data.first_labeled_target = target  # 대상 저장
                    first_labeled_data.first_labeled_expression = expression  # 현상 저장
                    first_labeled_data.review_id = Review.objects.get(pk=review_id)
                    first_labeled_data.category_id = Category.objects.get(pk=category_id)
                    first_labeled_data.save()

                # Next 버튼을 눌렀을 때
                if request.method == "GET" and request.GET.get("form-type") == 'NextForm':
                    review_id = request.GET.get('review_id')

                    # 해당 review의 작업 상태와 작업자를 변경
                    Review.objects.filter(pk=review_id).update(first_status=True, labeled_user_id=request.user)

                return render(request, 'labelingapp/labeling_work.html', context)

            return render(request, 'labelingapp/labeling_work.html')

        else:
            context = {'message': '제품, 범위를 다시 선택해주세요.'}
            return render(request, 'labelingapp/labeling_work.html', context)

    # 예외처리
    except Exception as identifier:
        print(identifier)

    return render(request, 'labelingapp/labeling_work.html')


def labeling_inspect(request):
    return render(request, 'labelingapp/labeling_inspect.html')