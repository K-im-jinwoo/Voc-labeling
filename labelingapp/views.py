from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render

# Create your views here.
from django.urls import reverse, resolve
from django.views.decorators.csrf import csrf_exempt

from mainapp.models import Category, Review, FirstLabeledData, SecondLabeledData


# start~end 범위 내 처리 안된 데이터 보여줌
def print_review(start, end, category_product):
    print_review_list = Review.objects.filter(category_product=category_product,
                                              review_number__range=(int(start), int(end)),
                                              first_status=False, second_status=False, dummy_status=False).order_by(
        'review_number')[:1]
    return print_review_list


def print_inspect(start, end, category_product):
    print_review_inspect = Review.objects.filter(category_product=category_product,
                                                 review_number__range=(int(start), int(end)),
                                                 first_status=True, second_status=False, dummy_status=False).order_by(
        'review_number')[:1]
    return print_review_inspect


@csrf_exempt
def delete_label(request):
    print('실행!')
    print(request.GET['label_number'])
    FirstLabeledData.objects.filter(pk=request.GET['label_number']).delete()
    return JsonResponse(data={})


@csrf_exempt
def delete_inspect_label(request):
    print('검수쪽 삭제부 실행되는 중')
    print(request.GET['label_number'])
    SecondLabeledData.objects.filter(pk=request.GET['label_number']).delete()
    return JsonResponse(data={})


@csrf_exempt
def reset(request):
    print('작업 쪽 초기화 작업')
    print(request.GET['review_id'])
    FirstLabeledData.objects.filter(review_id=request.GET['review_id']).delete()
    return JsonResponse(data={})


@csrf_exempt
def inspect_reset(request):
    print('검수 쪽 초기화 작업')
    print(request.GET['review_id'])
    FirstLabeledData.objects.filter(review_id=request.GET['review_id']).delete()
    SecondLabeledData.objects.filter(review_id=request.GET['review_id']).delete()
    return JsonResponse(data={})


def labeling_work(request):
    try:

        # reqeust한 URL의 파라미터에 제품군, 시작위치, 끝 위치가 있으면 데이터를 반환함
        if 'category_product' in request.GET and 'start' in request.GET and 'end' in request.GET:

            # 청소기, 냉장고, 식기세척기 제품군 선택 시에만 수행
            if request.GET['category_product'] in ['cleaner', 'refrigerator', 'dish_washer']:

                #####---- 해당 리뷰 불러오기 ----#####
                category_product = request.GET['category_product']
                start = request.GET['start']
                end = request.GET['end']
                category_detail = Category.objects.filter(category_product=category_product)

                if request.GET.get("form-type") == 'DummyForm':
                    review_id = request.GET.get('review_id')
                    Review.objects.filter(pk=review_id).update(first_status=False, dummy_status=True,
                                                               labeled_user_id=request.user)
                    FirstLabeledData.objects.filter(review_id=review_id).delete()

                #####---- 자동 라벨링 기능 ----#####
                # 자동 라벨링 - 검색
                review_first = print_review(start, end, category_product)

                # 자동 라벨링 - 저장
                if 'auto_labeling_status' not in request.session:
                    current_review = review_first[0].review_content
                    compare_data = FirstLabeledData.objects.filter(review_id__category_product=category_product)
                    auto_data_id = []
                    for i in compare_data:
                        if current_review.__contains__(i.first_labeled_target) and current_review.__contains__(
                                i.first_labeled_expression) and i.first_labeled_target != '' and i.first_labeled_expression != '':
                            if i.first_labeled_target not in compare_data.filter(pk__in=auto_data_id).values_list(
                                    'first_labeled_target', flat=True):
                                if i.first_labeled_expression not in compare_data.filter(
                                        pk__in=auto_data_id).values_list('first_labeled_expression', flat=True):
                                    auto_data_id.append(i.pk)
                    auto_data = compare_data.filter(pk__in=auto_data_id)
                    request.session['auto_labeling_status'] = review_first[0].review_id
                    for data in auto_data:
                        print('current auto labeling 지금 실행됨')
                        auto = FirstLabeledData()
                        auto.first_labeled_emotion = data.first_labeled_emotion  # 긍정 ,부정, 중립 저장
                        auto.first_labeled_target = data.first_labeled_target  # 대상 저장
                        auto.first_labeled_expression = data.first_labeled_expression  # 현상 저장
                        auto.review_id = Review.objects.get(pk=review_first[0].pk)
                        auto.category_id = data.category_id
                        auto.save()

                elif request.session['auto_labeling_status'] != review_first[0].review_id:
                    current_review = review_first[0].review_content
                    compare_data = FirstLabeledData.objects.filter(review_id__category_product=category_product)
                    auto_data_id = []
                    for i in compare_data:
                        if current_review.__contains__(i.first_labeled_target) and current_review.__contains__(
                                i.first_labeled_expression) and i.first_labeled_target != '' and i.first_labeled_expression != '':
                            if i.first_labeled_target not in compare_data.filter(pk__in=auto_data_id).values_list(
                                    'first_labeled_target', flat=True):
                                if i.first_labeled_expression not in compare_data.filter(
                                        pk__in=auto_data_id).values_list('first_labeled_expression', flat=True):
                                    auto_data_id.append(i.pk)
                    auto_data = compare_data.filter(pk__in=auto_data_id)
                    for data in auto_data:
                        auto = FirstLabeledData()
                        auto.first_labeled_emotion = data.first_labeled_emotion  # 긍정 ,부정, 중립 저장
                        auto.first_labeled_target = data.first_labeled_target  # 대상 저장
                        auto.first_labeled_expression = data.first_labeled_expression  # 현상 저장
                        auto.review_id = Review.objects.get(pk=review_first[0].pk)
                        auto.category_id = data.category_id
                        auto.save()
                    request.session['auto_labeling_status'] = review_first[0].review_id

                # 해당 제품군과 범위 중 제일 처음 한 개만 가져옴 => print_review() 함수 사용
                review_first = print_review(start, end, category_product)

                status_result = FirstLabeledData.objects.filter(review_id=review_first[0].pk)

                # labeling_work.html에 보낼 context 데이터
                context = {'category_detail': category_detail, 'category_product': category_product,
                           'review_first': review_first, 'start': start, 'end': end, 'status_result': status_result}

                # POST 방식 request 받았을 때 수행함.
                if request.method == "POST" and 'labeled_expression' in request.POST and 'labeled_target' in request.POST:
                    # 들어온 값 변수에 저장
                    target = request.POST.get('labeled_target')
                    emotion = request.POST.get('labeled_emotion')
                    expression = request.POST.get('labeled_expression')
                    review_id = request.POST.get('review_id')  # 해당 리뷰 id 받아오기
                    category_id = request.POST.get('category_id')  # 해당하는 리뷰에 맞는 카테고리id를 받아오기
                    print(target, emotion, expression)
                    if not FirstLabeledData.objects.filter(first_labeled_emotion=emotion, first_labeled_target=target,
                                                           first_labeled_expression=expression,
                                                           category_id=category_id, review_id=review_id):
                        # First_Labeled_Data모델을 불러와서 first_labeled_data에 저장
                        first_labeled_data = FirstLabeledData()

                        # laveling_work에서 불러온 값들을 first_labeled_data 안에 정해진 db이름으로 넣음
                        first_labeled_data.first_labeled_emotion = emotion  # 긍정 ,부정, 중립 저장
                        first_labeled_data.first_labeled_target = target  # 대상 저장
                        first_labeled_data.first_labeled_expression = expression  # 현상 저장
                        first_labeled_data.review_id = Review.objects.get(pk=review_id)
                        first_labeled_data.category_id = Category.objects.get(pk=category_id)
                        first_labeled_data.save()

                    wpp = '/labeling/work/?' + 'category_product=' + category_product + '&start=' + start + '&end=' + end
                    print("경로", wpp)
                    return HttpResponseRedirect(wpp)

                # Next 버튼을 눌렀을 때
                if request.method == "GET" and request.GET.get("form-type") == 'NextForm':
                    #####---- 리뷰 상태 변경 ----####
                    review_id = request.GET.get('review_id')
                    Review.objects.filter(pk=review_id).update(first_status=True, labeled_user_id=request.user)
                    review_first = print_review(start, end, category_product)

                    ######---- 자동 라벨링 ----#####
                    # 자동라벨링 - 저장
                    if ('auto_labeling_status' in request.session and request.session['auto_labeling_status'] !=
                            review_first[0].review_id):
                        current_review = review_first[0].review_content
                        compare_data = FirstLabeledData.objects.filter(review_id__category_product=category_product)
                        auto_data_id = []
                        for i in compare_data:
                            if current_review.__contains__(i.first_labeled_target) and current_review.__contains__(
                                    i.first_labeled_expression) and i.first_labeled_target != '' and i.first_labeled_expression != '':
                                if i.first_labeled_target not in compare_data.filter(pk__in=auto_data_id).values_list(
                                        'first_labeled_target', flat=True):
                                    if i.first_labeled_expression not in compare_data.filter(
                                            pk__in=auto_data_id).values_list('first_labeled_expression', flat=True):
                                        auto_data_id.append(i.pk)
                        auto_data = compare_data.filter(pk__in=auto_data_id)
                        for data in auto_data:
                            print('current auto labeling 지금 실행됨')
                            auto = FirstLabeledData()
                            auto.first_labeled_emotion = data.first_labeled_emotion  # 긍정 ,부정, 중립 저장
                            auto.first_labeled_target = data.first_labeled_target  # 대상 저장
                            auto.first_labeled_expression = data.first_labeled_expression  # 현상 저장
                            auto.review_id = Review.objects.get(pk=review_first[0].pk)
                            auto.category_id = data.category_id
                            auto.save()
                        request.session['auto_labeling_status'] = review_first[0].review_id
                    elif 'auto_labeling_status' not in request.session:
                        current_review = review_first[0].review_content
                        compare_data = FirstLabeledData.objects.filter(review_id__category_product=category_product)
                        auto_data_id = []
                        for i in compare_data:
                            if current_review.__contains__(i.first_labeled_target) and current_review.__contains__(
                                    i.first_labeled_expression) and i.first_labeled_target != '' and i.first_labeled_expression != '':
                                if i.first_labeled_target not in compare_data.filter(pk__in=auto_data_id).values_list(
                                        'first_labeled_target', flat=True):
                                    if i.first_labeled_expression not in compare_data.filter(
                                            pk__in=auto_data_id).values_list('first_labeled_expression', flat=True):
                                        auto_data_id.append(i.pk)
                        auto_data = compare_data.filter(pk__in=auto_data_id)
                        for data in auto_data:
                            print('current auto labeling 지금 실행됨')
                            auto = FirstLabeledData()
                            auto.first_labeled_emotion = data.first_labeled_emotion  # 긍정 ,부정, 중립 저장
                            auto.first_labeled_target = data.first_labeled_target  # 대상 저장
                            auto.first_labeled_expression = data.first_labeled_expression  # 현상 저장
                            auto.review_id = Review.objects.get(pk=review_first[0].pk)
                            auto.category_id = data.category_id
                            auto.save()
                        request.session['auto_labeling_status'] = review_first[0].review_id
                    status_result = FirstLabeledData.objects.filter(review_id=review_first[0].pk)

                    context = {'category_detail': category_detail, 'category_product': category_product,
                               'review_first': review_first, 'start': start, 'end': end, 'status_result': status_result}

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
    try:

        # reqeust한 URL의 파라미터에 제품군, 시작위치, 끝 위치가 있으면 데이터를 반환함
        if 'category_product' in request.GET and 'start' in request.GET and 'end' in request.GET:

            # 청소기, 냉장고, 식기세척기 제품군 선택 시에만 수행
            if request.GET['category_product'] in ['cleaner', 'refrigerator', 'dish_washer']:
                category_product = request.GET['category_product']
                start = request.GET['start']
                end = request.GET['end']
                category_detail = Category.objects.filter(category_product=category_product)

                if request.GET.get("form-type") == 'DummyForm':
                    print('여기')
                    review_id = request.GET.get('review_id')
                    Review.objects.filter(pk=review_id).update(second_status=False, dummy_status=True,
                                                               labeled_user_id=request.user)
                    SecondLabeledData.objects.filter(review_id=review_id).delete()

                # 해당 제품군과 범위 중 제일 처음 한 개만 가져옴 => print_inspect() 함수 사용
                review_first = print_inspect(start, end, category_product)
                status_result = FirstLabeledData.objects.filter(review_id=review_first[0].pk)
                status_result2 = SecondLabeledData.objects.filter(review_id=review_first[0].pk)

                # labeling_inspect.html에 보낼 context 데이터
                context = {'category_detail': category_detail, 'category_product': category_product,
                           'review_first': review_first, 'start': start, 'end': end, 'status_result': status_result,
                           'status_result2': status_result2}

                # POST 방식 request 받았을 때 수행함.
                if request.method == "POST" and 'labeled_expression' in request.POST and 'labeled_target' in request.POST:
                    # 들어온 값 변수에 저장
                    target = request.POST.get('labeled_target')
                    emotion = request.POST.get('labeled_emotion')
                    expression = request.POST.get('labeled_expression')
                    review_id = request.POST.get('review_id')  # 해당 리뷰 id 받아오기
                    category_id = request.POST.get('category_id')  # 해당하는 리뷰에 맞는 카테고리id를 받아오기
                    print(target, emotion, expression)

                    # SecondLabeledData모델을 불러와서 second_labeled_data에 저장
                    second_labeled_data = SecondLabeledData()

                    # laveling_inspect에서 불러온 값들을 second_labeled_data 안에 정해진 db이름으로 넣음
                    second_labeled_data.second_labeled_emotion = emotion  # 긍정 ,부정, 중립 저장
                    second_labeled_data.second_labeled_target = target  # 대상 저장
                    second_labeled_data.second_labeled_expression = expression  # 현상 저장
                    second_labeled_data.review_id = Review.objects.get(pk=review_id)
                    second_labeled_data.category_id = Category.objects.get(pk=category_id)
                    second_labeled_data.save()

                    pp = '/labeling/inspect/?' + 'category_product=' + category_product + '&start=' + start + '&end=' + end
                    print("경로", pp)

                    return HttpResponseRedirect(pp)

                # Next 버튼을 눌렀을 때
                if request.method == "GET" and request.GET.get("form-type") == 'NextForm':
                    review_id = request.GET.get('review_id')
                    first_data = FirstLabeledData.objects.filter(review_id=review_id)
                    print(first_data)
                    # 해당 리뷰에 관한 쌍들이 FirstLabeledData안에 있는 경우 SecondLabeledData로 복사하는 작업
                    for first_data in first_data:
                        f_e = first_data.first_labeled_emotion
                        f_t = first_data.first_labeled_target
                        f_ex = first_data.first_labeled_expression
                        f_c = first_data.category_id
                        f_r = first_data.review_id
                        print(f_e, f_t, f_ex, f_c, f_r)

                        # SecondLabeledData모델을 불러와서 second_labeled_data에 저장
                        second_labeled_data = SecondLabeledData()

                        # 저장한 값들을 second_labeled_data 안에 넣음
                        second_labeled_data.second_labeled_emotion = f_e  # 긍정 ,부정, 중립 저장
                        second_labeled_data.second_labeled_target = f_t  # 대상 저장
                        second_labeled_data.second_labeled_expression = f_ex  # 현상 저장
                        second_labeled_data.review_id = Review.objects.get(pk=f_r.pk)
                        second_labeled_data.category_id = Category.objects.get(pk=f_c.pk)
                        second_labeled_data.save()

                    # 해당 review의 작업 상태와 작업자를 변경(검수작업을 끝낸것을 표현)
                    Review.objects.filter(pk=review_id).update(second_status=True, labeled_user_id=request.user)

                    # 검수에서 다음 버튼을 누를시, 다음으로 올 리뷰를 미리 알고 해당하는 데이터쌍을 불러옴
                    next_review = print_inspect(start, end, category_product)
                    status_result = FirstLabeledData.objects.filter(review_id=next_review)

                    # labeling_inspect.html에 보낼 context 데이터
                    context = {'category_detail': category_detail, 'category_product': category_product,
                               'review_first': review_first, 'start': start, 'end': end, 'status_result': status_result}
                    return render(request, 'labelingapp/labeling_inspect.html', context)

                return render(request, 'labelingapp/labeling_inspect.html', context)

            return render(request, 'labelingapp/labeling_inspect.html')

        else:
            context = {'message': '제품, 범위를 다시 선택해주세요.'}
            return render(request, 'labelingapp/labeling_inspect.html', context)

    # 예외처리
    except Exception as identifier:
        print(identifier)

    return render(request, 'labelingapp/labeling_inspect.html')


def dummydummy(request):
    FirstLabeledData.objects.filter(first_labeled_target='시간', first_labeled_expression='2시간').delete()
    FirstLabeledData.objects.filter(first_labeled_target='시간', first_labeled_expression='오래').delete()
    FirstLabeledData.objects.filter(first_labeled_target='세척', first_labeled_expression='만족',
                                    category_id__category_product='dish_washer').delete()
    return render(request, 'mainapp/main_page.html')
