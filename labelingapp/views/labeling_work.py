from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F, Q

from mainapp.models import Category, Review, FirstLabeledData, WebStatus


def print_review(category_product, request):
    review = Review.objects.filter(category_product=category_product, first_status=0, second_status=0, dummy_status=0,
                                   first_assign_user=request.user.pk).order_by('review_number')[:1]
    return review


@csrf_exempt
def reset(request):
    print('작업 쪽 초기화 작업')
    print(request.GET['review_id'])
    FirstLabeledData.objects.filter(review_id=request.GET['review_id']).delete()
    return JsonResponse(data={})


@csrf_exempt
def delete_label(request):
    print('실행!')
    print(request.GET['label_number'])
    FirstLabeledData.objects.filter(pk=request.GET['label_number']).delete()
    return JsonResponse(data={})


def labeling_work(request):
    try:
        context = dict()
        context['product_names'] = Category.objects.all().values('category_product').distinct()
        auto_assignment_value = WebStatus.objects.get(status_name='auto_assignment_value').status_value
        auto_assignment_status = WebStatus.objects.get(status_name='auto_assignment_status').status_value

        # reqeust한 URL의 파라미터에 제품군, 시작위치, 끝 위치가 있으면 데이터를 반환함
        if 'category_product' in request.GET and request.GET['category_product']:
            category_product = request.GET['category_product']
            category_detail = Category.objects.filter(category_product=category_product)


            auto_assignment = auto_assignment_status == "True"
            manual_assignment = auto_assignment_status == "False" and 'assignment_count' in request.GET

            if not Review.objects.filter(
                category_product=category_product, first_status=0, second_status=0,
                dummy_status=0, first_assign_user=request.user.pk
            ).exists():
                review_assignment = Review.objects.filter(
                    category_product=category_product, first_status=0, second_status=0,
                    dummy_status=0, first_assign_user=0
                ).order_by('review_number').values('pk')[:int(auto_assignment_value if auto_assignment else request.GET.get('assignment_count'))]

                review_assignment.update(
                    first_assign_user=request.user.pk if request.user.pk is not None else "0"
                )

            if request.GET.get("form-type") == 'DummyForm':
                review_id = request.GET.get('review_id')
                Review.objects.filter(pk=review_id).update(first_status=False, dummy_status=True,
                                                            labeled_user_id=request.user)
                FirstLabeledData.objects.filter(review_id=review_id).delete()

            #####---- 자동 라벨링 기능 ----#####
            review_first = print_review(category_product, request)

            if 'auto_labeling_status' not in request.session:
                current_review = review_first[0].review_content

                auto_data = FirstLabeledData.objects.filter(
                    review_id__category_product=category_product,
                    first_labeled_target__isnull=False,
                    first_labeled_expression__isnull=False,
                    first_labeled_target__in=current_review,
                    first_labeled_expression__in=current_review
                ).exclude(pk__in=request.session.get('auto_labeling_status', []))

                request.session['auto_labeling_status'] = list(auto_data.values_list('pk', flat=True))

                auto_labels = [
                    FirstLabeledData(
                        first_labeled_emotion=data.first_labeled_emotion,
                        first_labeled_target=data.first_labeled_target,
                        first_labeled_expression=data.first_labeled_expression,
                        review_id=Review.objects.get(pk=review_first[0].pk),
                        category_id=data.category_id,
                        model_name=Review.objects.get(pk=review_first[0].pk).model_name,
                        model_code=Review.objects.get(pk=review_first[0].pk).model_code
                    ) for data in auto_data
                ]

                FirstLabeledData.objects.bulk_create(auto_labels)



            # 해당 제품군과 범위 중 제일 처음 한 개만 가져옴 => print_review() 함수 사용
            review_first = print_review(category_product, request)

            status_result = FirstLabeledData.objects.filter(review_id=review_first[0].pk)

            # labeling_work.html에 보낼 context 데이터
            context['category_detail'] = category_detail
            context['category_product'] = category_product
            assignment_count = Review.objects.filter(
                category_product=category_product, first_status=0, second_status=0, dummy_status=0,
                first_assign_user=request.user.pk
            ).order_by('review_number').count()
            context['review_first'] = review_first
            context['status_result'] = status_result

            if request.method == "POST" and 'labeled_expression' in request.POST and 'labeled_target' in request.POST:
                # POST 방식 요청 처리
                target = request.POST.get('labeled_target')
                emotion = request.POST.get('labeled_emotion')
                expression = request.POST.get('labeled_expression')
                review_id = request.POST.get('review_id')
                category_id = request.POST.get('category_id')
                print(target, emotion, expression)

                if not FirstLabeledData.objects.filter(
                    first_labeled_emotion=emotion, first_labeled_target=target,
                    first_labeled_expression=expression,
                    category_id=category_id, review_id=review_id
                ):
                    first_labeled_data = FirstLabeledData(
                        first_labeled_emotion=emotion,
                        first_labeled_target=target,
                        first_labeled_expression=expression,
                        review_id=Review.objects.get(pk=review_id),
                        category_id=Category.objects.get(pk=category_id),
                        model_code=Review.objects.get(pk=review_id).model_code,
                        model_name=Review.objects.get(pk=review_id).model_name
                    )
                    first_labeled_data.save()

                wpp = '/labeling/work/?category_product=' + category_product
                return HttpResponseRedirect(wpp)


            # Next 버튼을 눌렀을 때
            if request.method == "GET" and request.GET.get("form-type") == 'NextForm':
                review_id = request.GET.get('review_id')
                review = Review.objects.get(pk=review_id)

                # 리뷰 상태 변경
                review.first_status = True
                review.labeled_user_id = request.user
                review.save()

                review_first = print_review(category_product, request)
                current_review = review_first[0].review_content

                # 자동 라벨링 - 데이터 필터링 및 중복 제거
                compare_data = FirstLabeledData.objects.filter(
                    review_id__category_product=category_product,
                    first_labeled_target__isnull=False,
                    first_labeled_expression__isnull=False
                )

                auto_data_id = set()

                for i in compare_data:
                    if (
                        current_review.__contains__(i.first_labeled_target)
                        and current_review.__contains__(i.first_labeled_expression)
                    ):
                        auto_data_id.add(i.pk)

                auto_data = compare_data.filter(pk__in=auto_data_id)

                auto_data_list = []

                for data in auto_data:
                    auto_data_list.append(
                        FirstLabeledData(
                            first_labeled_emotion=data.first_labeled_emotion,
                            first_labeled_target=data.first_labeled_target,
                            first_labeled_expression=data.first_labeled_expression,
                            review_id=review,
                            category_id=data.category_id,
                            model_name=review.model_name,
                            model_code=review.model_code,
                        )
                    )

                FirstLabeledData.objects.bulk_create(auto_data_list)
                request.session['auto_labeling_status'] = review_first[0].review_id

                status_result = FirstLabeledData.objects.filter(review_id=review_first[0].pk)


                context['category_detail'] = category_detail
                context['category_product'] = category_product
                context['review_first'] = review_first
                context['status_result'] = status_result

            return render(request, 'labelingapp/labeling_work.html', context)


        else:
            context = dict()
            context['product_names'] = Category.objects.all().values('category_product').distinct()
            context['message'] = '제품, 범위를 다시 선택해주세요.'
            return render(request, 'labelingapp/labeling_work.html', context)

    # 예외처리
    except Exception as identifier:
        print(identifier)
        context = dict()
        context['product_names'] = Category.objects.all().values('category_product').distinct()

        return render(request, 'labelingapp/labeling_work.html', context)
