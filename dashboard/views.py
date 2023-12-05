from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from main import models as main_models


def type_to_variable(what_type, positive, negative, neutral, everything):
    variable = None
    if what_type == "positive":
        variable = positive
    elif what_type == "negative":
        variable = negative
    elif what_type == "neutral":
        variable = neutral
    elif what_type == "everything":
        variable = everything
    return variable


def sorting(sort, category_detail_list, positive, negative, neutral, everything):
    standard = []

    # 정렬 기준을 standard 리스트에 추가
    if sort == "positive":
        standard = [p.count() for p in positive]
    elif sort == "negative":
        standard = [n.count() for n in negative]
    elif sort == "neutral":
        standard = [neu.count() for neu in neutral]
    elif sort == "everything":
        standard = [e.count() for e in everything]

    # 내림차순 정렬
    for i in range(len(standard) - 1):
        for j in range(i + 1, len(standard)):
            if standard[i] < standard[j]:
                category_detail_list[i], category_detail_list[j] = (
                    category_detail_list[j],
                    category_detail_list[i],
                )
                positive[i], positive[j] = positive[j], positive[i]
                negative[i], negative[j] = negative[j], negative[i]
                neutral[i], neutral[j] = neutral[j], neutral[i]
                everything[i], everything[j] = everything[j], everything[i]
                standard[i], standard[j] = standard[j], standard[i]

@csrf_exempt
def dashboard(request):
    try:
        if "category_model_code" in request.GET:
            (
                category_model_code,
                category_product,
                category_model_name,
            ) = request.GET.get("category_model_code").split(",")
            category_model_code = (
                category_model_code.replace("{", "").replace("}", "").replace('"', "")
            )
            category_product = (
                category_product.replace("{", "").replace("}", "").replace('"', "")
            )
            category_model_name = (
                category_model_name.replace("{", "").replace("}", "").replace('"', "")
            )
            if "sort" not in request.session:
                request.session["sort"] = "positive"
                # 해당 제품군의 카테고리 정보 불러옴
            category_detail = main_models.Category.objects.filter(category_product=category_product)
            alltotal = (
                main_models.Review.objects.filter(category_product=category_product)
                .filter(model_name=category_model_name)
                .filter(model_code=category_model_code)
                .count()
            )
            first_num = (
                main_models.Review.objects.filter(category_product=category_product)
                .filter(first_status=True)
                .filter(model_name=category_model_name)
                .filter(model_code=category_model_code)
                .count()
            )
            second_num = (
                main_models.Review.objects.filter(category_product=category_product)
                .filter(second_status=True)
                .filter(model_name=category_model_name)
                .filter(model_code=category_model_code)
                .count()
            )
            dummy_num = (
                main_models.Review.objects.filter(category_product=category_product)
                .filter(dummy_status=True)
                .filter(model_name=category_model_name)
                .filter(model_code=category_model_code)
                .count()
            )
            left = alltotal - first_num

            """카테고리별 긍정 부정 개수"""
            context = {}
            category_detail_list = []
            positive = []
            negative = []
            neutral = []
            everything = []
            order = []
            i = 0

            # 카테고리별 라벨링된 데이터 개수 불러옴(개수 아니기 때문에 바로 쓰시면 됩니다.)
            for category in category_detail:
                positive_temp = (
                    main_models.FirstLabeledData.objects.filter(
                        category_id=category, first_labeled_emotion="positive"
                    )
                    .filter(model_name=category_model_name)
                    .filter(model_code=category_model_code)
                )
                negative_temp = (
                    main_models.FirstLabeledData.objects.filter(
                        category_id=category, first_labeled_emotion="negative"
                    )
                    .filter(model_name=category_model_name)
                    .filter(model_code=category_model_code)
                )
                neutral_temp = (
                    main_models.FirstLabeledData.objects.filter(
                        category_id=category, first_labeled_emotion="neutral"
                    )
                    .filter(model_name=category_model_name)
                    .filter(model_code=category_model_code)
                )
                everything_temp = (
                    main_models.FirstLabeledData.objects.filter(category_id=category)
                    .filter(model_name=category_model_name)
                    .filter(model_code=category_model_code)
                )

                category_detail_list.append(category.category_middle)
                positive.append(positive_temp)
                negative.append(negative_temp)
                neutral.append(neutral_temp)
                everything.append(everything_temp)
                order.append(i)
                i += 1

            # 정렬 요청 들어오면 session에 정렬 요구 상태 저장
            if request.method == "POST" and "sort" in request.POST:
                sort = request.POST.get("sort")
                request.session["sort"] = sort

            # session에 저장한 요구 상태를 읽어 정렬 수행
            if request.session["sort"] != "sort":
                sorting(
                    request.session["sort"],
                    category_detail_list,
                    positive,
                    negative,
                    neutral,
                    everything,
                )

            elif request.session["sort"] == "sort":
                sorting(
                    "positive",
                    category_detail_list,
                    positive,
                    negative,
                    neutral,
                    everything,
                )

            # 번호 개수를 눌렀을 때 (대상, 현상)과 원문데이터 보여줌
            if request.method == "GET" and "showing_index" in request.GET:
                # 번호의 위치(showing_index)와 번호의 긍부정 여부(showing_type)을 가져옴
                showing_index = request.GET.get("showing_index")
                showing_type = request.GET.get("showing_type")

                # labeled_word에 대상 - 현상 키워드 쌍을 저장함
                labeled_word = type_to_variable(
                    showing_type, positive, negative, neutral, everything
                )
                labeled_word = labeled_word[int(showing_index)]
                set_labeled_word = labeled_word
                labeled_box = []
                box_counter = []
                for obj in set_labeled_word:
                    target = obj.first_labeled_target
                    expression = obj.first_labeled_expression
                    ssang = [target, expression]
                    if ssang not in labeled_box:
                        labeled_box.append(ssang)
                        ssang_name = target + expression
                        box_counter.append({ssang_name: 1})
                    else:
                        key_to_find = ssang_name
                        for dictionary in box_counter:
                            if key_to_find in dictionary:
                                dictionary[ssang_name] += 1
                for box in labeled_box:
                    sum = box[0] + box[1]
                    for d in box_counter:
                        a = d.keys()
                        if next(iter(a)) == sum:
                            box.append(next(iter(d.values())))

                # labeled_word = list(set(labeled_word))
                context["box"] = labeled_box
                context["box_counter"] = box_counter

                context["labeled_word"] = labeled_word
                # 번호 눌렀을 때 리뷰 원문 데이터 보여주기
                labeled_review = labeled_word.values_list("review_id", flat=True)
                labeled_review = main_models.Review.objects.filter(pk__in=labeled_review)
                context["labeled_review"] = labeled_review

            data = zip(
                category_detail_list, positive, negative, neutral, everything, order
            )
            data1 = zip(
                category_detail_list, positive, negative, neutral, everything, order
            )
            data_list = list(data1)
            category_detail_list = [item[0] for item in data_list]
            positive = [item[1] for item in data_list]
            negative = [item[2] for item in data_list]
            neutral = [item[3] for item in data_list]

            # positive 변수 출력
            context = {
                # 다른 데이터도 추가할 수 있음
                "negative": negative,
                "neutral": neutral,
                "everything": everything,
                "order": order,
            }
            results_positive = []
            results_negative = []
            results_neutral = []

            for queryset in positive:
                result = queryset.filter(first_labeled_emotion="positive").count()
                results_positive.append(result if result else 0)

            for queryset in negative:
                result = queryset.filter(first_labeled_emotion="negative").count()
                results_negative.append(result if result else 0)

            for queryset in neutral:
                result = queryset.filter(first_labeled_emotion="neutral").count()
                results_neutral.append(result if result else 0)

            context = {
                "category_detail_list": category_detail_list,
                "results_positive": results_positive,
                "results_negative": results_negative,
                "results_neutral": results_neutral,
            }

            context["data"] = data
            context["category_product"] = category_product
            context["alltotal"] = alltotal
            context["first_num"] = first_num
            context["dummy_num"] = dummy_num
            context["second_num"] = second_num
            context["left"] = alltotal - first_num
            context["product_names"] = (
                main_models.Category.objects.all().values("category_product").distinct()
            )

            my_model_list = (
                main_models.Review.objects.filter(category_product=category_product)
                .values("model_name")
                .distinct()
            )
            context["model_names"] = my_model_list
            context["selected_name"] = category_model_name
            context["selected"] = category_product
            my_code_list = (
                main_models.Review.objects.filter(
                    category_product=category_product, model_name=category_model_name
                )
                .values("model_code")
                .distinct()
            )
            context["model_codes"] = my_code_list
            context["selected_code"] = category_model_code

            return render(request, "dashboard.html", context=context)
        elif "category_model_name" in request.GET:
            category_model_name, selected = request.GET.get(
                "category_model_name"
            ).split(",")
            category_model_name = (
                category_model_name.replace("{", "").replace("}", "").replace('"', "")
            )
            selected = selected.replace("{", "").replace("}", "").replace('"', "")
            category_product = selected
            if "sort" not in request.session:
                request.session["sort"] = "positive"
                # 해당 제품군의 카테고리 정보 불러옴
            category_detail = main_models.Category.objects.filter(category_product=category_product)
            alltotal = (
                main_models.Review.objects.filter(category_product=category_product)
                .filter(model_name=category_model_name)
                .count()
            )
            first_num = (
                main_models.Review.objects.filter(category_product=category_product)
                .filter(first_status=True)
                .filter(model_name=category_model_name)
                .count()
            )
            second_num = (
                main_models.Review.objects.filter(category_product=category_product)
                .filter(second_status=True)
                .filter(model_name=category_model_name)
                .count()
            )
            dummy_num = (
                main_models.Review.objects.filter(category_product=category_product)
                .filter(dummy_status=True)
                .filter(model_name=category_model_name)
                .count()
            )

            """카테고리별 긍정 부정 개수"""
            context = {}
            category_detail_list = []
            positive = []
            negative = []
            neutral = []
            everything = []
            order = []
            i = 0

            # 카테고리별 라벨링된 데이터 개수 불러옴(개수 아니기 때문에 바로 쓰시면 됩니다.)
            for category in category_detail:
                positive_temp = main_models.FirstLabeledData.objects.filter(
                    category_id=category, first_labeled_emotion="positive"
                ).filter(model_name=category_model_name)
                negative_temp = main_models.FirstLabeledData.objects.filter(
                    category_id=category, first_labeled_emotion="negative"
                ).filter(model_name=category_model_name)
                neutral_temp = main_models.FirstLabeledData.objects.filter(
                    category_id=category, first_labeled_emotion="neutral"
                ).filter(model_name=category_model_name)
                everything_temp = main_models.FirstLabeledData.objects.filter(
                    category_id=category
                ).filter(model_name=category_model_name)

                category_detail_list.append(category.category_middle)
                positive.append(positive_temp)
                negative.append(negative_temp)
                neutral.append(neutral_temp)
                everything.append(everything_temp)
                order.append(i)
                i += 1
            # 정렬 요청 들어오면 session에 정렬 요구 상태 저장
            if request.method == "POST" and "sort" in request.POST:
                sort = request.POST.get("sort")
                request.session["sort"] = sort
            data1 = zip(
                category_detail_list, positive, negative, neutral, everything, order
            )
            data_list = list(data1)

            category_detail_list = [item[0] for item in data_list]
            positive = [item[1] for item in data_list]
            negative = [item[2] for item in data_list]
            neutral = [item[3] for item in data_list]

            # positive 변수 출력
            context = {
                # 다른 데이터도 추가할 수 있음
                "negative": negative,
                "neutral": neutral,
                "everything": everything,
                "order": order,
            }
            results_positive = []
            results_negative = []
            results_neutral = []

            for queryset in positive:
                result = queryset.filter(first_labeled_emotion="positive").count()
                results_positive.append(result if result else 0)

            for queryset in negative:
                result = queryset.filter(first_labeled_emotion="negative").count()
                results_negative.append(result if result else 0)

            for queryset in neutral:
                result = queryset.filter(first_labeled_emotion="neutral").count()
                results_neutral.append(result if result else 0)

            context = {
                "category_detail_list": category_detail_list,
                "results_positive": results_positive,
                "results_negative": results_negative,
                "results_neutral": results_neutral,
            }

            # session에 저장한 요구 상태를 읽어 정렬 수행
            if request.session["sort"] != "sort":
                sorting(
                    request.session["sort"],
                    category_detail_list,
                    positive,
                    negative,
                    neutral,
                    everything,
                )

            elif request.session["sort"] == "sort":
                sorting(
                    "positive",
                    category_detail_list,
                    positive,
                    negative,
                    neutral,
                    everything,
                )

            # 번호 개수를 눌렀을 때 (대상, 현상)과 원문데이터 보여줌
            if request.method == "GET" and "showing_index" in request.GET:
                # 번호의 위치(showing_index)와 번호의 긍부정 여부(showing_type)을 가져옴
                showing_index = request.GET.get("showing_index")
                showing_type = request.GET.get("showing_type")

                # labeled_word에 대상 - 현상 키워드 쌍을 저장함
                labeled_word = type_to_variable(
                    showing_type, positive, negative, neutral, everything
                )
                labeled_word = labeled_word[int(showing_index)]

                set_labeled_word = labeled_word
                labeled_box = []
                box_counter = []
                for obj in set_labeled_word:
                    target = obj.first_labeled_target
                    expression = obj.first_labeled_expression
                    ssang = [target, expression]
                    if ssang not in labeled_box:
                        labeled_box.append(ssang)
                        ssang_name = target + expression
                        box_counter.append({ssang_name: 1})
                    else:
                        key_to_find = ssang_name
                        for dictionary in box_counter:
                            if key_to_find in dictionary:
                                dictionary[ssang_name] += 1
                for box in labeled_box:
                    sum = box[0] + box[1]
                    for d in box_counter:
                        a = d.keys()
                        if next(iter(a)) == sum:
                            box.append(next(iter(d.values())))

                # labeled_word = list(set(labeled_word))
                context["box"] = labeled_box
                context["box_counter"] = box_counter
                context["labeled_word"] = labeled_word
                # 번호 눌렀을 때 리뷰 원문 데이터 보여주기
                labeled_review = labeled_word.values_list("review_id", flat=True)
                labeled_review = main_models.Review.objects.filter(pk__in=labeled_review)
                context["labeled_review"] = labeled_review

            data = zip(
                category_detail_list, positive, negative, neutral, everything, order
            )

            context["data"] = data
            context["category_product"] = category_product
            context["alltotal"] = alltotal
            context["first_num"] = first_num
            context["dummy_num"] = dummy_num
            context["second_num"] = second_num
            context["left"] = alltotal - first_num
            context["product_names"] = (
                main_models.Category.objects.all().values("category_product").distinct()
            )

            my_model_list = (
                main_models.Review.objects.filter(category_product=category_product)
                .values("model_name")
                .distinct()
            )
            context["model_names"] = my_model_list
            context["selected_name"] = category_model_name
            my_code_list = (
                main_models.Review.objects.filter(
                    category_product=category_product, model_name=category_model_name
                )
                .values("model_code")
                .distinct()
            )
            context["model_codes"] = my_code_list
            context["selected"] = category_product

            return render(request, "dashboard.html", context=context)

            ###########################################################################################################################
        # reqeust한 URL의 파라미터에 제품군, 시작위치, 끝 위치가 있으면 데이터를 반환함
        elif "category_product" in request.GET:
            # 청소기, 냉장고, 식기세척기 제품군 선택 시에만 수행
            if request.GET.get("category_product"):
                category_product = request.GET["category_product"]

                global cp
                cp = category_product

                if "sort" not in request.session:
                    request.session["sort"] = "positive"
                # 해당 제품군의 카테고리 정보 불러옴
                category_product = request.GET["category_product"]
                category_detail = main_models.Category.objects.filter(
                    category_product=category_product
                )
                alltotal = main_models.Review.objects.filter(
                    category_product=category_product
                ).count()
                first_num = (
                    main_models.Review.objects.filter(category_product=category_product)
                    .filter(first_status=True)
                    .count()
                )
                second_num = (
                    main_models.Review.objects.filter(category_product=category_product)
                    .filter(second_status=True)
                    .count()
                )
                dummy_num = (
                    main_models.Review.objects.filter(category_product=category_product)
                    .filter(dummy_status=True)
                    .count()
                )

                """카테고리별 긍정 부정 개수"""
                context = {}
                category_detail_list = []
                positive = []
                negative = []
                neutral = []
                everything = []
                order = []
                i = 0

                # 카테고리별 라벨링된 데이터 개수 불러옴(개수 아니기 때문에 바로 쓰시면 됩니다.)
                for category in category_detail:
                    positive_temp = main_models.FirstLabeledData.objects.filter(
                        category_id=category, first_labeled_emotion="positive"
                    )
                    negative_temp = main_models.FirstLabeledData.objects.filter(
                        category_id=category, first_labeled_emotion="negative"
                    )
                    neutral_temp = main_models.FirstLabeledData.objects.filter(
                        category_id=category, first_labeled_emotion="neutral"
                    )
                    everything_temp = main_models.FirstLabeledData.objects.filter(
                        category_id=category
                    )

                    category_detail_list.append(category.category_middle)
                    positive.append(positive_temp)
                    negative.append(negative_temp)
                    neutral.append(neutral_temp)
                    everything.append(everything_temp)
                    order.append(i)
                    i += 1

                # 정렬 요청 들어오면 session에 정렬 요구 상태 저장
                if request.method == "POST" and "sort" in request.POST:
                    sort = request.POST.get("sort")
                    request.session["sort"] = sort

                # session에 저장한 요구 상태를 읽어 정렬 수행

                if request.session["sort"] != "sort":
                    sorting(
                        request.session["sort"],
                        category_detail_list,
                        positive,
                        negative,
                        neutral,
                        everything,
                    )

                elif request.session["sort"] == "sort":
                    sorting(
                        "positive",
                        category_detail_list,
                        positive,
                        negative,
                        neutral,
                        everything,
                    )

                # 번호 개수를 눌렀을 때 (대상, 현상)과 원문데이터 보여줌
                if request.method == "GET" and "showing_index" in request.GET:
                    # 번호의 위치(showing_index)와 번호의 긍부정 여부(showing_type)을 가져옴
                    showing_index = request.GET.get("showing_index")
                    showing_type = request.GET.get("showing_type")

                    # labeled_word에 대상 - 현상 키워드 쌍을 저장함
                    labeled_word = type_to_variable(
                        showing_type, positive, negative, neutral, everything
                    )
                    labeled_word = labeled_word[int(showing_index)]
                    set_labeled_word = labeled_word
                    labeled_box = []
                    box_counter = []

                    for obj in set_labeled_word:
                        target = obj.first_labeled_target
                        expression = obj.first_labeled_expression
                        ssang = [target, expression]
                        if ssang not in labeled_box:
                            labeled_box.append(ssang)
                            ssang_name = target + expression
                            box_counter.append({ssang_name: 1})
                        else:
                            key_to_find = ssang_name
                            for dictionary in box_counter:
                                if key_to_find in dictionary:
                                    dictionary[ssang_name] += 1
                    for box in labeled_box:
                        sum = box[0] + box[1]
                        for d in box_counter:
                            a = d.keys()
                            if next(iter(a)) == sum:
                                box.append(next(iter(d.values())))

                    # labeled_word = list(set(labeled_word))
                    context["box"] = labeled_box
                    context["box_counter"] = box_counter
                    context["labeled_word"] = labeled_word
                    # 번호 눌렀을 때 리뷰 원문 데이터 보여주기
                    labeled_review = labeled_word.values_list("review_id", flat=True)
                    labeled_review = main_models.Review.objects.filter(pk__in=labeled_review)
                    context["labeled_review"] = labeled_review

                select_categorys = main_models.Category.objects.filter(
                    category_product=category_product
                ).values("category_id")

                select_ids = main_models.FirstLabeledData.objects.filter(
                    category_id__in=select_categorys
                ).values("review_id")
                # 선택한 카테고리의 리뷰id 활용해서 해당 contents만 뽑기
                select_reviews_list = list(
                    main_models.Review.objects.filter(category_product=cp)
                    .filter(review_id__in=select_ids)
                    .values_list("review_content", flat=True)
                )
                # 선택한 카테고리의 대상
                select_targets_list = list(
                    main_models.FirstLabeledData.objects.filter(
                        category_id__in=select_categorys
                    ).values_list("first_labeled_target", flat=True)
                )
                # 선택한 카테고리의 현상
                select_expression_list = list(
                    main_models.FirstLabeledData.objects.filter(
                        category_id__in=select_categorys
                    ).values_list("first_labeled_expression", flat=True)
                )
                select_expression = select_expression_list
                for target in select_targets_list:
                    select_expression_list.append(target)

                context = dict()

                data = zip(
                    category_detail_list, positive, negative, neutral, everything, order
                )
                data1 = zip(
                    category_detail_list, positive, negative, neutral, everything, order
                )
                data_list = list(data1)

                # 리스트 안에 있는 정보들 전부 다담기
                category_detail_list = [item[0] for item in data_list]
                positive = [item[1] for item in data_list]
                negative = [item[2] for item in data_list]
                neutral = [item[3] for item in data_list]

                # positive 변수 출력
                context = {
                    # 다른 데이터도 추가할 수 있음
                    "negative": negative,
                    "neutral": neutral,
                    "everything": everything,
                    "order": order,
                }
                results_positive = []
                results_negative = []
                results_neutral = []
                # print하면 쿼리셋으로 나오는데 쿼리셋에 나오는 positive 갯수 list에 다 담았음
                for queryset in positive:
                    result = queryset.filter(first_labeled_emotion="positive").count()
                    results_positive.append(result if result else 0)

                for queryset in negative:
                    result = queryset.filter(first_labeled_emotion="negative").count()
                    results_negative.append(result if result else 0)

                for queryset in neutral:
                    result = queryset.filter(first_labeled_emotion="neutral").count()
                    results_neutral.append(result if result else 0)

                context = {
                    "category_detail_list": category_detail_list,
                    "results_positive": results_positive,
                    "results_negative": results_negative,
                    "results_neutral": results_neutral,
                    "select_expression": select_expression,
                    "select_reviews": select_reviews_list,
                }
                global state
                state = context
                context["data"] = data
                context["all_category_list"] = category_detail_list
                context["category_detail_list"] = category_detail_list
                context["category_product"] = category_product
                context["alltotal"] = alltotal
                context["first_num"] = first_num
                context["dummy_num"] = dummy_num
                context["second_num"] = second_num
                context["left"] = alltotal - first_num
                context["product_names"] = (
                    main_models.Category.objects.all().values("category_product").distinct()
                )

                my_model_list = (
                    main_models.Review.objects.filter(category_product=category_product)
                    .values("model_name")
                    .distinct()
                )
                context["model_names"] = my_model_list
                context["selected"] = category_product

                return render(request, "dashboard.html", context=context)
            context = dict()
            context["product_names"] = (
                main_models.Category.objects.all().values("category_product").distinct()
            )
            return render(request, "dashboard.html", context=context)

        elif request.method == "POST":
            # 선택한 카테고리
            checked_data = request.POST.getlist("checked_data[]")
            common_indices = [
                state["category_detail_list"].index(category)
                for category in checked_data
                if category in state["category_detail_list"]
            ]

            # 해당 카테고리에 속하는 모든 리뷰 중에서 firstlabeleddata 값이 존재하는 리뷰만 추출
            select_category = (
                main_models.Review.objects.filter(
                    category_product=cp, firstlabeleddata__isnull=False
                )
                .values("firstlabeleddata")
                .distinct()
            )

            q = Q()
            for category in checked_data:
                q |= Q(category_middle=category)
            # Category모델에서 category_product와 우리가 선택한 product와 비교해 해당 카테고리 들고오기, 그 중에서 q로 필터링하기, value로 해당하는 category_id 들고옴
            select_categorys = (
                main_models.Category.objects.filter(category_product=cp)
                .filter(q)
                .values("category_id")
            )
            # 선택한 카테고리의 리뷰 id
            select_ids = main_models.FirstLabeledData.objects.filter(
                category_id__in=select_categorys
            ).values("review_id")
            # 선택한 카테고리의 리뷰id 활용해서 해당 contents만 뽑기
            select_reviews_list = list(
                main_models.Review.objects.filter(category_product=cp)
                .filter(review_id__in=select_ids)
                .values_list("review_content", flat=True)
            )
            # 선택한 카테고리의 대상
            select_targets_list = list(
                main_models.FirstLabeledData.objects.filter(
                    category_id__in=select_categorys
                ).values_list("first_labeled_target", flat=True)
            )
            # 선택한 카테고리의 현상
            select_expression_list = list(
                main_models.FirstLabeledData.objects.filter(
                    category_id__in=select_categorys
                ).values_list("first_labeled_expression", flat=True)
            )
            # <-- 선택한 카테고리 target emotion
            select_target_positive = list(
                main_models.FirstLabeledData.objects.filter(
                    category_id__in=select_categorys, first_labeled_emotion="positive"
                ).values_list("first_labeled_target", flat=True)
            )
            select_target_negative = list(
                main_models.FirstLabeledData.objects.filter(
                    category_id__in=select_categorys, first_labeled_emotion="negative"
                ).values_list("first_labeled_target", flat=True)
            )
            select_target_neutral = list(
                main_models.FirstLabeledData.objects.filter(
                    category_id__in=select_categorys, first_labeled_emotion="neutral"
                ).values_list("first_labeled_target", flat=True)
            )
            # --> 선택한 카테고리 target emotion

            # <-- 선택한 카테고리 expression emotion
            select_expression_positive = list(
                main_models.FirstLabeledData.objects.filter(
                    category_id__in=select_categorys, first_labeled_emotion="positive"
                ).values_list("first_labeled_expression", flat=True)
            )
            select_expression_negative = list(
                main_models.FirstLabeledData.objects.filter(
                    category_id__in=select_categorys, first_labeled_emotion="negative"
                ).values_list("first_labeled_expression", flat=True)
            )
            select_expression_neutral = list(
                main_models.FirstLabeledData.objects.filter(
                    category_id__in=select_categorys, first_labeled_emotion="neutral"
                ).values_list("first_labeled_expression", flat=True)
            )
            # --> 선택한 카테고리 expression emotion

            # 추출된 리뷰의 모든 firstlabeleddata 값을 추출하여 리스트로 변환
            first_values = [
                category["firstlabeleddata"] for category in select_category
            ]

            # 모든 first_values에 해당하는 main_models.FirstLabeledData를 추출
            # 이 때 distinct()를 사용하여 중복된 데이터를 제거하고, values() 메서드를 사용하여 first_labeled_target 값만 추출
            first_targets = (
                main_models.FirstLabeledData.objects.filter(first_labeled_id__in=first_values)
                .distinct()
                .values("first_labeled_target")
            )
            first_expression = main_models.FirstLabeledData.objects.filter(
                first_labeled_id__in=first_values
            ).values("first_labeled_expression")
            first_emotion = main_models.FirstLabeledData.objects.filter(
                first_labeled_id__in=first_values
            ).values("first_labeled_emotion")
            categoryId = main_models.FirstLabeledData.objects.filter(
                first_labeled_id__in=first_values
            ).values("category_id")
            # categoryMiddle = Category.objects.filter(categoty_id=categoryId).values("category_middle")

            target_list = [query["first_labeled_target"] for query in first_targets]
            expression_list = [
                query["first_labeled_expression"] for query in first_expression
            ]
            # 어짜피 한 리스트로 쓸거라 두 배열을 합침
            for target in select_targets_list:
                select_expression_list.append(target)

            context = dict()
            context["all_category_list"] = state["category_detail_list"]
            context["select_reviews"] = select_reviews_list
            # 선택한 카테고리의 현상
            context["select_expression"] = select_expression_list

            select_expression_dict = {}
            for word in select_expression_list:
                if word in select_expression_dict:
                    select_expression_dict[word] += 1
                else:
                    select_expression_dict[word] = 1
            context["select_expression_dict"] = select_expression_dict

            # 선택한 카테고리의 대상
            context["select_targets"] = select_targets_list

            select_targets_dict = {}
            for word in select_targets_list:
                if word in select_targets_dict:
                    select_targets_dict[word] += 1
                else:
                    select_targets_dict[word] = 1
            context["select_targets_dict"] = select_targets_dict
            # context["target_list"] = target_list

            # 선택한 타겟 카테고리 긍정
            target_positive_dict = {}
            for word in select_target_positive:
                if word in target_positive_dict:
                    target_positive_dict[word] += 1
                else:
                    target_positive_dict[word] = 1
            context["target_positive_dict"] = target_positive_dict
            # 선택한 카테고리 부정
            target_negative_dict = {}
            for word in select_target_negative:
                if word in target_negative_dict:
                    target_negative_dict[word] += 1
                else:
                    target_negative_dict[word] = 1
            context["target_negative_dict"] = target_negative_dict
            # 선택한 카테고리 중립
            target_neutral_dict = {}
            for word in select_target_neutral:
                if word in target_neutral_dict:
                    target_neutral_dict[word] += 1
                else:
                    target_neutral_dict[word] = 1
            context["target_neutral_dict"] = target_neutral_dict

            # 선택한 현상 카테고리 긍정
            expression_positive_dict = {}
            for word in select_expression_positive:
                if word in expression_positive_dict:
                    expression_positive_dict[word] += 1
                else:
                    expression_positive_dict[word] = 1
            context["expression_positive_dict"] = expression_positive_dict
            # 선택한 현상 카테고리 부정
            expression_negative_dict = {}
            for word in select_expression_negative:
                if word in expression_negative_dict:
                    expression_negative_dict[word] += 1
                else:
                    expression_negative_dict[word] = 1
            context["expression_negative_dict"] = expression_negative_dict
            # 선택한 현상 카테고리 중립
            expression_neutral_dict = {}
            for word in select_expression_neutral:
                if word in expression_neutral_dict:
                    expression_neutral_dict[word] += 1
                else:
                    expression_neutral_dict[word] = 1
            context["expression_neutral_dict"] = expression_neutral_dict

            context["select_category"] = select_category

            category_detail_list = []
            results_positive = []
            results_negative = []
            results_neutral = []

            for key, value in state.items():
                if isinstance(value, list):  # value가 리스트인 키들만 추출합니다.
                    # 해당하는 키의 인덱스 번호들만 추출합니다.
                    indices = [i for i, x in enumerate(value) if i in common_indices]
                    # 추출한 인덱스 번호들에 해당하는 데이터들을 출력합니다.
                    selected_data = [value[i] for i in indices]

                    if key == "category_detail_list":
                        category_detail_list = selected_data
                    elif key == "results_positive":
                        results_positive = selected_data
                    elif key == "results_negative":
                        results_negative = selected_data
                    elif key == "results_neutral":
                        results_neutral = selected_data
            context["category_detail_list"] = category_detail_list
            context["results_positive"] = results_positive
            context["results_negative"] = results_negative
            context["results_neutral"] = results_neutral
            context["product_names"] = (
                main_models.Category.objects.all().values("category_product").distinct()
            )
            context["checked_data"] = checked_data

            #트리맵 클릭한 제품명 ajax로 가져오기 
            treemap_name = request.POST.get('treemap_name')
            
            if treemap_name:
                category = main_models.Category.objects.get(category_middle=treemap_name)
                
                first_labeled_data_list = main_models.FirstLabeledData.objects.filter(category_id=category)
                
                review_list = main_models.Review.objects.filter(review_id__in=first_labeled_data_list.values("review_id"))
                review_contents = []

                for review in review_list:
                    review_contents.append(review.review_content)

                response_data = {
                    'selected_reviews': review_contents,
                }

                return JsonResponse(response_data)

            return render(request, "dashboard.html", context=context)

        else:
            context = {"message": "제품을 다시 선택해주세요."}
            context["product_names"] = (
                main_models.Category.objects.all().values("category_product").distinct()
            )
            return render(
                request,
                "dashboard.html",
                context=context,
            )

    # 예외처리
    except Exception as identifier:
        print(identifier)
    context = dict()
    return render(request, "dashboard.html", context=context)
