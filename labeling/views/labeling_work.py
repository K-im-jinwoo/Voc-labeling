from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from main import models as main_models

# 할당된 제일 최근 리뷰 데이터와 자동 라벨링 해주는 함수
@csrf_exempt
def find_review_auto_labeling(product, user):

    # 첫번째 데이터
    first_data = main_models.Review.objects.filter(
        product__name=product, assigned_user=main_models.Profile.objects.get(user=user), is_labeled=False, is_trashed=False
        ).order_by("id").first()
    
    # 기존 데이터
    exist_datas = main_models.LabelingData.objects.filter(category__product__name=product)
    
    # 자동 라벨링 데이터 리스트
    auto_labeling_datas = []
    for exist_data in exist_datas:
        if first_data.content.__contains__(exist_data.target) and first_data.content.__contains__(exist_data.phenomenon):
            auto_labeling_datas.append(
                {
                    "category": exist_data.category.name,
                    "category_color": exist_data.category.color,
                    "target": exist_data.target,
                    "phenomenon": exist_data.phenomenon,
                    "emotion": exist_data.emotion.k_name
                }
            )

    review_auto_labeling = {
        "id": first_data.id,
        "content": first_data.content,
        "auto_labeling": auto_labeling_datas
    }

    # 프론트에게 넘겨 줄 데이터 형식 => review_auto_labeling
	# review_auto_labeling = {
	# 	"id": int,
	# 	"content": "--------",
	# 	"auto_labeling": [
	# 		{"category": "", "category_color": "", "target": "" , "phenomenon": "", "emtion": ""},
	# 		{"category": "", "category_color": "", "target": "" , "phenomenon": "", "emtion": ""},
	# 		...
	# 	]
    # }
    return review_auto_labeling

# 라벨링 페이지의 모든 동작
@csrf_exempt
def labeling_work(request):
    try:
        context=dict()
        if request.method == "GET":
            if "product_name" in request.GET: # 할당 -> 리뷰데이터 + 자동라벨링 보여주는 파트
                context = dict()

                # is_assigned=True인 경우(이미 할당된 데이터가 있으므로 할당 작업을 제외하고 바로 review데이터 보내기)
                # is_assigned=False 경우(할당된 데이터가 없으므로 할당 작업을 거치고 review데이터 보내기)
                if not request.GET["is_assigned"]:
                    # review에 해당 user들을 할당시킴(count수만큼)
                    pass
                review = find_review_auto_labeling(request.GET["product_name"], request.user)
                context["review"] = review

            ## labeling page 탭을 누르고 처음 들어왔을 경우 기본적으로 프론트한테 전달해야하는 데이터 -> 프론트가 보관해두고 계속 써야할 데이터
            elif "product_name" not in request.GET:
                # login된 user
                current_user = request.user

                # 모든 Product
                qs_product = main_models.Product.objects.all()

                # 모든 Category
                qs_category = main_models.Category.objects.select_related("product").all()

                # assign정보를 알기위해 모든 review를 가져옴
                qs_review = main_models.Review.objects.select_related("product", "assigned_user__user").all()

                # product_names
                product_names = []
                for product in qs_product:
                    product_names.append({
                        "product_name": product.name,
                        # review 데이터중 해당 제품과 assigned_user가 현재 유저인 경우가 존재하는지에 대한 필드
                        "is_assigned": qs_review.filter(product=product, assigned_user__user=current_user).exists(), 
                        "assigned_num": qs_review.filter(product=product, assigned_user__user=current_user).count()
                    })

                # category_list
                category_list = {}
                for product in qs_product:
                    categories_by_product = qs_category.filter(product=product)
                    name_color_list=[]
                    for category in categories_by_product:
                        name_color_list.append({"name":category.name, "color":category.color})
                    category_list[product.name] = name_color_list

                # emotion
                emotion = main_models.Emotion.objects.all().values_list("e_name", flat=True)

                context["product_names"] = product_names
                context["category_list"] = category_list
                context["emotion"] = list(emotion)

            return render(request, "labeling/labeling_work.html", context=context)
        
        elif request.method == "POST":
            if request.GET.get("form-type") == "LabelingForm": # 라벨링 작업
                # 프론트에서 받아야할 데이터
                # labeling_data_list = [
                #     {
                #         "review_id": [int],
                #         "prouct": 필요할 것 같음 -> 프론트에 물어보기
                #         "category": "",
                #         "target": "",
                #         "phenomenon": "",
                #         "emtion": ""
                #     }, ...
                # ]
                labeling_data_list = []

                qs_categories = main_models.Category.objects.filter(product__name=product)

                # 작업 데이터 저장
                for labeling_data in labeling_data_list:
                    main_models.LabelingData.objects.create(
                        review_id=labeling_data["review_id"],
                        category=qs_categories.filter(name=labeling_data["category"]),
                        emotion__e_name=labeling_data["emotion"],
                        target=labeling_data["target"],
                        phenomenon=labeling_data["phenomenon"]
                    )
                
                # 리뷰의 라벨링 상태 업데이트 -> review_id를 가져오는 부분을 수정해야할 것 같음
                main_models.Review.objects.get(id=review_id).update(assigned_user=None, is_labeled=True)
            
            elif request.GET.get("form-type") == "DummyForm": # 리뷰 -> is_trashed=True작업
                # 프론트에서 받아야 할 데이터
                # {
                #     "review_id": int
                # }
                review_id = request.POST.get("review_id")

                # 테스트 결과 이렇게 하면 정상 작동하지만, profile이 존재해야만 정상 작동.
                main_models.Review.objects.filter(id=review_id).update(assigned_user=None, is_trashed=True, worked_user=main_models.Profile.objects.get(user=request.user))
            

            # 다음 리뷰와 자동 라벨링 데이터 가져오기
            review = find_review_auto_labeling(product, request.user)
            context["review"] = review
            return render(request, "labeling/labeling_work.html", context=context)

    # 예외처리
    except Exception as identifier:
        print(identifier)
    context = dict()
    return render(request, "labeling/labeling_work.html", context=context)







# 기존 라벨링 페이지 예시보고 리팩토링 진행(아래 함수는 참고용)
def ex_labeling_work(request):
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
