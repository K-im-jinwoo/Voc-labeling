from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from mainapp.models import Review, SecondLabeledData, FirstLabeledData, Category


def print_inspect(start, end, category_product):
    print_review_inspect = Review.objects.filter(category_product=category_product,
                                                 review_number__range=(int(start), int(end)),
                                                 first_status=True, second_status=False, dummy_status=False).order_by(
        'review_number')[:1]
    return print_review_inspect


@csrf_exempt
def delete_inspect_label(request):
    print('검수쪽 삭제부 실행되는 중')
    print(request.GET['label_number'])
    SecondLabeledData.objects.filter(pk=request.GET['label_number']).delete()
    return JsonResponse(data={})


@csrf_exempt
def delete_label(request):
    print('실행!')
    print(request.GET['label_number'])
    FirstLabeledData.objects.filter(pk=request.GET['label_number']).delete()
    return JsonResponse(data={})


@csrf_exempt
def inspect_reset(request):
    print('검수 쪽 초기화 작업')
    print(request.GET['review_id'])
    FirstLabeledData.objects.filter(review_id=request.GET['review_id']).delete()
    SecondLabeledData.objects.filter(review_id=request.GET['review_id']).delete()
    return JsonResponse(data={})


def labeling_inspect(request):
    try:
        context = dict()
        context['product_names'] = Category.objects.all().values('category_product').distinct()
        # 제품군 선택 시 수행
        if 'category_product' in request.GET:
            #####---- 해당 리뷰 불러오기 ----#####
            category_product = request.GET['category_product']
            category_detail = Category.objects.filter(category_product=category_product)

            ####---- 할당된 데이터가 없는 경우 ----####
            if len(Review.objects.filter(category_product=category_product,first_status=True,dummy_status=False,
                            second_assign_user=request.user.pk,second_status=False)) == 0 and 'assignment' in request.GET:
                print("할당된 데이터가 없는 경우 실행")
                assignment = request.GET['assignment']
                if assignment == "ten":
                    assignment = int(10)
                elif assignment == "twenty":
                    assignment = int(20)
                elif assignment == "thirty":
                    assignment = int(30)
                else:
                    print('할당 실패')

                # print("할당 개수", assignment)
                review_assignment = Review.objects.filter(category_product=category_product,first_status=True,second_status=False,second_assign_user=0).values('pk')[:assignment]
                review_assignment = Review.objects.filter(pk__in=review_assignment)
                review_assignment.update(second_assign_user=request.user.pk)
                review_assignment = Review.objects.filter(category_product=category_product, second_assign_user=request.user.pk, second_status=False)

                print(review_assignment)
                review_data_couple = []
                for review_assignment_num in review_assignment:
                    print(review_assignment_num.pk)
                    data = list(FirstLabeledData.objects.filter(review_id=review_assignment_num.pk).values_list(
                        'first_labeled_target', 'first_labeled_expression', 'first_labeled_emotion'))
                    review_data_couple.append(data)
                print(review_data_couple)

                if len(review_assignment)==0:
                    print("작업된 데이터가 없습니다.")

            ####----할당된 데이터가 있는경우----####
            else:
                print("할당됐던 데이터 출력 성공")
                review_assignment = Review.objects.filter(category_product=category_product, second_assign_user=request.user.pk, second_status=False)

                review_data_couple = []
                for review_assignment_num in review_assignment:
                    print(review_assignment_num.pk)
                    data = list(FirstLabeledData.objects.filter(review_id=review_assignment_num.pk).values_list('first_labeled_target','first_labeled_expression','first_labeled_emotion'))
                    review_data_couple.append(data)
                print(review_data_couple)



            review_full_data = zip(review_assignment,review_data_couple)



            # labeling_inspect.html에 보낼 context 데이터
            context['review_full_data'] = review_full_data
            context['review_data_couple'] = review_data_couple
            context['review_assignment'] = review_assignment
            context['category_detail'] = category_detail
            context['category_product'] = category_product
            return render(request, 'labelingapp/labeling_inspect.html', context)

        ####----검수완료버튼 클릭----####
        elif request.method == "POST" and request.POST.get("form-type") == 'SuccessForm':
            print("검수완료 버튼 클릭")
            print(request.POST.get('category_product'))
            full_review = request.POST.getlist('full_review')
            check_review = request.POST.getlist('check_review')
            incomplete_review = list(set(full_review).difference(set(check_review)))

            print("검수단계의 모든 데이터 : full_review", full_review)
            print("검수작업 통과 데이터 : check_review", check_review)
            print("작업 전 단계로 돌릴 데이터 : incomplete_review", incomplete_review)


            #####---- 검수 완료 데이터 상태 변경(검수 완료) ----####
            for second_status_change_review in check_review:
                # print(second_status_change_review)
                Review.objects.filter(review_id=second_status_change_review).update(second_status=True, second_assign_user = 0)


            ####---- 작업 전 단계로 되돌릴 데이터 상태 변경 ----####
            for first_status_change_review in incomplete_review:
                print(first_status_change_review)
                Review.objects.filter(review_id=first_status_change_review).update(first_status=0,dummy_status=0,labeled_user_id=None,first_assign_user=0,second_assign_user=0)


            print("상태변경완료")
            return render(request, 'labelingapp/labeling_inspect.html', context)


        else:
            context = {'message': '제품, 범위를 다시 선택해주세요.'}
            context['product_names'] = Category.objects.all().values('category_product').distinct()
            return render(request, 'labelingapp/labeling_inspect.html', context)



    # 예외처리
    except Exception as identifier:
        print(identifier)
        return render(request, 'labelingapp/labeling_inspect.html')
