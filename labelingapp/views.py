from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.urls import reverse

from mainapp.models import Category, Review, FirstLabeledData


def print_review(start, end, category_product):
    print_review_list = Review.objects.filter(category_product=category_product,
                                              review_number__range=(int(start), int(end)),
                                              first_status=False, second_status=False, dummy_status=False).order_by(
        'review_number')[:1]
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

        elif request.method == "POST" and 'labeled_emotion' in request.POST: #긍,부정 라벨링 POST가 들어올때 동작

            #들어온 값 변수에 저장
            target = request.POST.get('labeled_target')
            emotion = request.POST.get('labeled_emotion')
            expression = request.POST.get('labeled_expression')
            print(target, emotion, expression)

            # First_Labeled_Data모델을 불러와서 first_labeled_data에 저장
            first_labeled_data=FirstLabeledData()
            review_detail = request.POST.get('review_number') #해당 리뷰 번호 받아오기
            print(review_detail)
            # laveling_work에서 불러온 값들을 first_labeled_data 안에 정해진 db이름으로 넣음
            first_labeled_data.first_labeled_emotion = emotion #긍,부정 저장
            first_labeled_data.first_labeled_target = target # 대상 저장
            first_labeled_data.first_labeled_expression = expression #현상 저장


            category_ID = request.POST.get('category_id') # 해당하는 리뷰에 맞는 카테고리와 리뷰 id를 받아오는 법 찾아야할듯(같은수정필요)
            # 지금까지 받아온 값 firstlabeleddata(First_Labeled_Data DB)에 저장
            print(category_ID)
            first_labeled_data.save()
            #
            # 상태(True,False) 업데이트해서 Review DB에 다시 저장 (수정필요,업데이트 방법 찾아야함)
            # obj2 = Review.objects.filter(pk='review_id').update(first_status=True,
            #                                                          labeled_user_id=request.user)
            # obj2 = review_detail.review_id
            # obj2.first_status = True
            # obj2.save()



            return #다음 리뷰 불러오기?

        else:
            return HttpResponse("아무것도 해당안됨")



    # 예외처리
    except Exception as identifier:
        print(identifier)

    return render(request, 'labelingapp/labeling_work.html')


def labeling_inspect(request):
    return render(request, 'labelingapp/labeling_inspect.html')

