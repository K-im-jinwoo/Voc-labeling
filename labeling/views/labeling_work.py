from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from main import models as main_models


def print_review(category_product, request):
    review = main_models.Review.objects.filter(
        category_product=category_product,
        first_status=0,
        second_status=0,
        dummy_status=0,
        first_assign_user=request.user.pk,
    ).order_by("review_number")[:1]
    return review


@csrf_exempt
def reset(request):
    print("작업 쪽 초기화 작업")
    print(request.GET["review_id"])
    main_models.LabelingData.objects.filter(
        review_id=request.GET["review_id"]
    ).delete()
    return JsonResponse(data={})


@csrf_exempt
def delete_label(request):
    print("실행!")
    print(request.GET["label_number"])
    main_models.LabelingData.objects.filter(pk=request.GET["label_number"]).delete()
    return JsonResponse(data={})


def labeling_work(request):
    try:
        context = dict()
        context["product_names"] = (
            main_models.Category.objects.all().values("category_product").distinct()
        )
        auto_assignment_value = main_models.WebStatus.objects.get(
            status_name="auto_assignment_value"
        ).status_value
        auto_assignment_status = main_models.WebStatus.objects.get(
            status_name="auto_assignment_status"
        ).status_value

        # reqeust한 URL의 파라미터에 제품군, 시작위치, 끝 위치가 있으면 데이터를 반환함
        if "category_product" in request.GET:
            print(request.GET)
            # 청소기, 냉장고, 식기세척기 제품군 선택 시에만 수행
            if request.GET.get("category_product"):
                #####---- 해당 리뷰 불러오기 ----#####
                category_product = request.GET["category_product"]
                category_detail = main_models.Category.objects.filter(
                    category_product=category_product
                )

                ##### ----- 라벨링 페이지 켜면 자동할당됨(자동 할당 상태일 경우) ----- #####
                if (
                    auto_assignment_status == "True"
                    and len(
                        main_models.Review.objects.filter(
                            category_product=category_product,
                            first_status=0,
                            second_status=0,
                            dummy_status=0,
                            first_assign_user=request.user.pk,
                        )
                    )
                    == 0
                ):
                    review_assignment = (
                        main_models.Review.objects.filter(
                            category_product=category_product,
                            first_status=0,
                            second_status=0,
                            dummy_status=0,
                            first_assign_user=0,
                        )
                        .order_by("review_number")
                        .values("pk")[: int(auto_assignment_value)]
                    )
                    review_assignment = main_models.Review.objects.filter(
                        pk__in=review_assignment
                    ).order_by("review_number")
                    review_assignment.update(
                        first_assign_user=request.user.pk
                        if request.user.pk != None
                        else "0"
                    )

                ##### ----- 개수 선택하면 할당됨(자동 할당 상태일 아닐 경우) ----- #####
                if (
                    auto_assignment_status == "False"
                    and len(
                        main_models.Review.objects.filter(
                            category_product=category_product,
                            first_status=0,
                            second_status=0,
                            dummy_status=0,
                            first_assign_user=request.user.pk,
                        )
                    )
                    == 0
                    and "assignment_count" in request.GET
                ):
                    review_assignment = (
                        main_models.Review.objects.filter(
                            category_product=category_product,
                            first_status=0,
                            second_status=0,
                            dummy_status=0,
                            first_assign_user=0,
                            second_assign_user=0,
                        )
                        .order_by("review_number")
                        .values("pk")[: int(request.GET.get("assignment_count"))]
                    )
                    print("1", len(review_assignment))
                    review_assignment = main_models.Review.objects.filter(
                        pk__in=review_assignment
                    ).order_by("review_number")
                    print("2", len(review_assignment))
                    review_assignment.update(
                        first_assign_user=request.user.pk
                        if request.user.pk != None
                        else "0"
                    )

                if request.GET.get("form-type") == "DummyForm":
                    review_id = request.GET.get("review_id")
                    main_models.Review.objects.filter(pk=review_id).update(
                        first_status=False,
                        dummy_status=True,
                        labeled_user_id=request.user,
                    )
                    main_models.LabelingData.objects.filter(
                        review_id=review_id
                    ).delete()

                #####---- 자동 라벨링 기능 ----#####
                # 자동 라벨링 - 검색
                review_first = print_review(category_product, request)

                # 자동 라벨링 - 저장
                if "auto_labeling_status" not in request.session:
                    current_review = review_first[0].review_content
                    compare_data = main_models.LabelingData.objects.filter(
                        review_id__category_product=category_product
                    )
                    auto_data_id = []
                    for i in compare_data:
                        if (
                            current_review.__contains__(i.first_labeled_target)
                            and current_review.__contains__(i.first_labeled_expression)
                            and i.first_labeled_target != ""
                            and i.first_labeled_expression != ""
                        ):
                            if i.first_labeled_target not in compare_data.filter(
                                pk__in=auto_data_id
                            ).values_list("first_labeled_target", flat=True):
                                if (
                                    i.first_labeled_expression
                                    not in compare_data.filter(
                                        pk__in=auto_data_id
                                    ).values_list("first_labeled_expression", flat=True)
                                ):
                                    auto_data_id.append(i.pk)
                    auto_data = compare_data.filter(pk__in=auto_data_id)
                    request.session["auto_labeling_status"] = review_first[0].review_id
                    for data in auto_data:
                        print("current auto labeling 지금 실행됨")
                        auto = main_models.LabelingData()
                        auto.first_labeled_emotion = (
                            data.first_labeled_emotion
                        )  # 긍정 ,부정, 중립 저장
                        auto.first_labeled_target = data.first_labeled_target  # 대상 저장
                        auto.first_labeled_expression = (
                            data.first_labeled_expression
                        )  # 현상 저장
                        auto.review_id = main_models.Review.objects.get(
                            pk=review_first[0].pk
                        )
                        auto.category_id = data.category_id
                        auto.model_name = main_models.Review.objects.get(
                            pk=review_first[0].pk
                        ).model_name
                        auto.model_code = main_models.Review.objects.get(
                            pk=review_first[0].pk
                        ).model_code
                        auto.save()

                elif (
                    request.session["auto_labeling_status"] != review_first[0].review_id
                ):
                    current_review = review_first[0].review_content
                    compare_data = main_models.LabelingData.objects.filter(
                        review_id__category_product=category_product
                    )
                    auto_data_id = []
                    for i in compare_data:
                        if (
                            current_review.__contains__(i.first_labeled_target)
                            and current_review.__contains__(i.first_labeled_expression)
                            and i.first_labeled_target != ""
                            and i.first_labeled_expression != ""
                        ):
                            if i.first_labeled_target not in compare_data.filter(
                                pk__in=auto_data_id
                            ).values_list("first_labeled_target", flat=True):
                                if (
                                    i.first_labeled_expression
                                    not in compare_data.filter(
                                        pk__in=auto_data_id
                                    ).values_list("first_labeled_expression", flat=True)
                                ):
                                    auto_data_id.append(i.pk)
                    auto_data = compare_data.filter(pk__in=auto_data_id)
                    for data in auto_data:
                        auto = main_models.LabelingData()
                        auto.first_labeled_emotion = (
                            data.first_labeled_emotion
                        )  # 긍정 ,부정, 중립 저장
                        auto.first_labeled_target = data.first_labeled_target  # 대상 저장
                        auto.first_labeled_expression = (
                            data.first_labeled_expression
                        )  # 현상 저장
                        auto.review_id = main_models.Review.objects.get(
                            pk=review_first[0].pk
                        )
                        auto.category_id = data.category_id
                        auto.model_name = main_models.Review.objects.get(
                            pk=review_first[0].pk
                        ).model_name
                        auto.model_code = main_models.Review.objects.get(
                            pk=review_first[0].pk
                        ).model_code
                        auto.save()
                    request.session["auto_labeling_status"] = review_first[0].review_id

                # 해당 제품군과 범위 중 제일 처음 한 개만 가져옴 => print_review() 함수 사용
                review_first = print_review(category_product, request)

                status_result = main_models.LabelingData.objects.filter(
                    review_id=review_first[0].pk
                )

                # labeling_work.html에 보낼 context 데이터
                context["category_detail"] = category_detail
                context["category_product"] = category_product
                assignment_count = (
                    main_models.Review.objects.filter(
                        category_product=category_product,
                        first_status=0,
                        second_status=0,
                        dummy_status=0,
                        first_assign_user=request.user.pk,
                    )
                    .order_by("review_number")
                    .count()
                )
                context["review_first"] = review_first
                context["status_result"] = status_result

                # POST 방식 request 받았을 때 수행함.
                if (
                    request.method == "POST"
                    and "labeled_expression" in request.POST
                    and "labeled_target" in request.POST
                ):
                    # 들어온 값 변수에 저장
                    target = request.POST.get("labeled_target")
                    emotion = request.POST.get("labeled_emotion")
                    expression = request.POST.get("labeled_expression")
                    review_id = request.POST.get("review_id")  # 해당 리뷰 id 받아오기
                    category_id = request.POST.get(
                        "category_id"
                    )  # 해당하는 리뷰에 맞는 카테고리id를 받아오기
                    print(target, emotion, expression)
                    if not main_models.LabelingData.objects.filter(
                        first_labeled_emotion=emotion,
                        first_labeled_target=target,
                        first_labeled_expression=expression,
                        category_id=category_id,
                        review_id=review_id,
                    ):
                        # First_Labeled_Data모델을 불러와서 first_labeled_data에 저장
                        first_labeled_data = main_models.LabelingData()

                        # labeling_work에서 불러온 값들을 first_labeled_data 안에 정해진 db이름으로 넣음
                        first_labeled_data.first_labeled_emotion = (
                            emotion  # 긍정 ,부정, 중립 저장
                        )
                        first_labeled_data.first_labeled_target = target  # 대상 저장
                        first_labeled_data.first_labeled_expression = (
                            expression  # 현상 저장
                        )
                        first_labeled_data.review_id = main_models.Review.objects.get(
                            pk=review_id
                        )
                        first_labeled_data.category_id = (
                            main_models.Category.objects.get(pk=category_id)
                        )
                        first_labeled_data.model_code = main_models.Review.objects.get(
                            pk=review_id
                        ).model_code
                        first_labeled_data.model_name = main_models.Review.objects.get(
                            pk=review_id
                        ).model_name

                        first_labeled_data.save()

                    wpp = "/labeling/work/?" + "category_product=" + category_product
                    return HttpResponseRedirect(wpp)

                # Next 버튼을 눌렀을 때
                if (
                    request.method == "GET"
                    and request.GET.get("form-type") == "NextForm"
                ):
                    review_id = request.GET.get("review_id")
                    review = main_models.Review.objects.get(pk=review_id)

                    # 리뷰 상태 변경
                    review.first_status = True
                    review.labeled_user_id = request.user
                    review.save()

                    review_first = print_review(category_product, request)

                    if (
                        "auto_labeling_status" in request.session
                        and request.session["auto_labeling_status"]
                        != review_first[0].review_id
                    ):
                        current_review = review_first[0].review_content

                        # 자동 라벨링 - 데이터 필터링 및 중복 제거
                        compare_data = main_models.LabelingData.objects.filter(
                            review_id__category_product=category_product,
                            first_labeled_target__isnull=False,
                            first_labeled_expression__isnull=False,
                        )

                        auto_data_id = set()

                        for i in compare_data:
                            if current_review.__contains__(
                                i.first_labeled_target
                            ) and current_review.__contains__(
                                i.first_labeled_expression
                            ):
                                auto_data_id.add(i.pk)

                        auto_data = compare_data.filter(pk__in=auto_data_id)

                        auto_data_list = []

                        for data in auto_data:
                            auto_data_list.append(
                                main_models.LabelingData(
                                    first_labeled_emotion=data.first_labeled_emotion,
                                    first_labeled_target=data.first_labeled_target,
                                    first_labeled_expression=data.first_labeled_expression,
                                    review_id=review,
                                    category_id=data.category_id,
                                    model_name=review.model_name,
                                    model_code=review.model_code,
                                )
                            )

                        main_models.LabelingData.objects.bulk_create(auto_data_list)
                        request.session["auto_labeling_status"] = review_first[
                            0
                        ].review_id
                    elif "auto_labeling_status" not in request.session:
                        current_review = review_first[0].review_content

                        # 자동 라벨링 - 데이터 필터링 및 중복 제거
                        compare_data = main_models.LabelingData.objects.filter(
                            review_id__category_product=category_product,
                            first_labeled_target__isnull=False,
                            first_labeled_expression__isnull=False,
                        )

                        auto_data_id = set()

                        for i in compare_data:
                            if current_review.__contains__(
                                i.first_labeled_target
                            ) and current_review.__contains__(
                                i.first_labeled_expression
                            ):
                                auto_data_id.add(i.pk)

                        auto_data = compare_data.filter(pk__in=auto_data_id)

                        auto_data_list = []

                        for data in auto_data:
                            auto_data_list.append(
                                main_models.LabelingData(
                                    first_labeled_emotion=data.first_labeled_emotion,
                                    first_labeled_target=data.first_labeled_target,
                                    first_labeled_expression=data.first_labeled_expression,
                                    review_id=review,
                                    category_id=data.category_id,
                                    model_name=review.model_name,
                                    model_code=review.model_code,
                                )
                            )

                        main_models.LabelingData.objects.bulk_create(auto_data_list)
                        request.session["auto_labeling_status"] = review_first[
                            0
                        ].review_id

                    status_result = main_models.LabelingData.objects.filter(
                        review_id=review_first[0].pk
                    )

                    context["category_detail"] = category_detail
                    context["category_product"] = category_product
                    context["review_first"] = review_first
                    context["status_result"] = status_result

                return render(request, "labeling/labeling_work.html", context)

        else:
            context = dict()
            context["product_names"] = (
                main_models.Category.objects.all().values("category_product").distinct()
            )
            context["message"] = "제품, 범위를 다시 선택해주세요."
            return render(request, "labeling/labeling_work.html", context)

    # 예외처리
    except Exception as identifier:
        print(identifier)
        context = dict()
        context["product_names"] = (
            main_models.Category.objects.all().values("category_product").distinct()
        )

        return render(request, "labeling/labeling_work.html", context)
