from django.db.models import Q, Count
from django.shortcuts import render

from main import models as main_models

def workstatus_review(request):
    try:
        context=dict()
        if request.method == "GET":
            if "product" in request.GET:
                product_name = request.GET.get("product")
                model_name = request.GET.get("model_name")
                model_code = request.GET.get("model_code")

                # 필터 생성
                filter_conditions = Q(product__name=product_name)
                filter_conditions_labeled_review = Q(review__product__name=product_name)

                # model_name이 존재하면 해당 조건 추가
                if model_name:
                    filter_conditions &= Q(model_name=model_name)
                    filter_conditions_labeled_review &= Q(review__model_name=model_name)

                # model_code가 존재하면 해당 조건 추가
                if model_code:
                    filter_conditions &= Q(model_code=model_code)
                    filter_conditions_labeled_review &= Q(review__model_code=model_code)

                # 총 개수
                total_count_query = main_models.Review.objects.filter(filter_conditions)
                context["total_count"] = total_count_query.count()
                # print("총 개수 ", context["total_count"])
                
                # 작업 완료 개수
                complete_count_query = total_count_query.filter(is_labeled=True)
                context["complete_count"] = complete_count_query.count()
                # print("작업 완료 개수 ", context["complete_count"])
                
                # 남은 개수
                remain_count_query = total_count_query.filter(is_labeled=False)
                context["remain_count"] = remain_count_query.count()
                # print("남은 개수 ", context["remain_count"])

                # 삭제 개수
                deleted_count_query = total_count_query.filter(is_trashed=True)
                context["deleted_count"] = deleted_count_query.count()
                # print("삭제 개수 ", context["deleted_count"])


                # 카테고리 리스트
                category_emotion_dict = {}
                category_list = main_models.Category.objects.filter(product__name=product_name).values_list("name", flat=True)
                for category in category_list:
                    emotion_count = main_models.LabelingData.objects.filter(category__name=category).filter(filter_conditions_labeled_review)
                    positive_count = emotion_count.filter(emotion__e_name="positive").count()
                    nagetive_count = emotion_count.filter(emotion__e_name="nagetive").count()
                    neutral_count = emotion_count.filter(emotion__e_name="neutral").count()
                    emotion_total_count = positive_count + nagetive_count + neutral_count
                    category_emotion_dict[category] = {"positive_count": positive_count, "negative_count": nagetive_count, "neutral_count": neutral_count, "emotion_total_count": emotion_total_count}
                context["category_emotion_dict"] = category_emotion_dict
                # print(category_emotion_dict)
                # {'기타': {'positive_count': 0, 'negative_count': 0, 'neutral_count': 0, 'emotion_total_count': 0}, '테스트 카테고리1': {'positive_count': 0, 'negative_count': 0, 'neutral_count': 0, 'emotion_total_count': 0}}

                # 정렬 요청이 들어오면
                if request.method == "POST" and "sort" in request.POST:
                    # 프론트에서 context["emotion"] 이걸 저장해놓고 하나를 보내주면
                    sort_pick = request.POST.get("sort")
                    key_mapping = {
                        "positive": "positive_count",
                        "negative": "nagative_count",
                        "neutral": "neutral_count",
                        "total": "emotion_total_count"
                    }
                    if sort_pick in key_mapping:
                        category_emotion_dict = dict(sorted(category_emotion_dict.items(), key=lambda x: x[1][key_mapping[sort_pick]], reverse=True))
                        context["sorted_category_emotion_dict"] = category_emotion_dict


                # 번호 개수를 눌렀을 때 (대상, 현상)과 원문데이터 보여줌
                if request.method == "GET" and "showing_index" in request.GET:
                    category_name = request.POST.get("category") # 카테고리 중 1개
                    emotion_name = request.POST.get("emotion") # positive, negative, neutral, total 중 1개
            
                    labeling_data_obj = main_models.LabelingData.objects.filter(filter_conditions_labeled_review).filter(category__name=category_name)
                    if emotion_name == "positive":
                        target_phenomenon = labeling_data_obj.filter(emotion__e_name="positive").values_list("target","phenomenon")
                        target_phenomenon_list = [f"{target}-{phenomenon}" for target, phenomenon in target_phenomenon]
                        print(target_phenomenon_list) #['test_target-test_phenomenon', '', ...]

                        review = labeling_data_obj.filter(emotion__e_name="positive").values_list("review__id" ,"review__content")
                        review_list =  [f"{review__id}-{review__content}" for review__id, review__content in review]
                        print(review_list) # ['28695-소음이 작아서 아주 도움 될꺼에요', '', ...]

                    elif emotion_name == "negative":
                        target_phenomenon =  labeling_data_obj.filter(emotion__e_name="negative").values_list("target","phenomenon")
                        target_phenomenon_list = [f"{target}-{phenomenon}" for target, phenomenon in target_phenomenon]

                        review = labeling_data_obj.filter(emotion__e_name="negative").values_list("review__id" ,"review__content")
                        review_list =  [f"{review__id}-{review__content}" for review__id, review__content in review]

                    elif emotion_name == "neutral":
                        target_phenomenon =  labeling_data_obj.filter(emotion__e_name="neutral").values_list("target","phenomenon")
                        target_phenomenon_list = [f"{target}-{phenomenon}" for target, phenomenon in target_phenomenon]

                        review = labeling_data_obj.filter(emotion__e_name="neutral").values_list("review__id" ,"review__content")
                        review_list =  [f"{review__id}-{review__content}" for review__id, review__content in review]

                    elif emotion_name == "total":
                        target_phenomenon = labeling_data_obj.values_list("target","phenomenon")
                        target_phenomenon_list = [f"{target}-{phenomenon}" for target, phenomenon in target_phenomenon]

                        review = labeling_data_obj.values_list("review__id" ,"review__content")
                        review_list =  [f"{review__id}-{review__content}" for review__id, review__content in review]

                    context["target_phenomenon_list"] = target_phenomenon_list
                    context["review_list"] = review_list


            elif "product" not in request.GET:
                qs_product = main_models.Product.objects.all()
                qs_review = main_models.Review.objects.all()
                qs_emotion = main_models.Emotion.objects.all()
                emotion_names = [emotion.e_name for emotion in qs_emotion] + ["total"]

                res_data= {}

                for product in qs_product:
                    model_data = {}
                    model_names_by_product = qs_review.filter(product=product).exclude(model_name="").values_list("model_name", flat=True).distinct()
                    for model_name in model_names_by_product:
                        model_codes = qs_review.filter(product=product, model_name=model_name).exclude(model_code="").values_list("model_code", flat=True).distinct()
                        model_data[model_name] = {"model_code": list(model_codes)}
            
                    res_data[product.name] = {"model_name": model_data}

                context["product"] = res_data
                context["emotion"] = emotion_names
                # 예시 형식 -> {'테스트 제품': {'model_name': {'모델네임1': {'model_code': ['모델코드1', '모델코드2']}, '모델네임2': {'model_code': ['모델코드3', '모델코드4']}}}
    
    # 예외처리
    except Exception as identifier:
        print(identifier)
    context = dict()
    return render(request, "main/workstatus_review.html", context=context)