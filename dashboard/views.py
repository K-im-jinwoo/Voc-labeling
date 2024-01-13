from datetime import datetime, timedelta
from django.db.models import Q, Count
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from main import models as main_models

def calculate_date_intervals(start_date, end_date, num_intervals):
    date_range = end_date - start_date
    interval = date_range // num_intervals
    return [{"start": start_date + i * interval, "end": start_date + (i + 1) * interval} for i in range(num_intervals)]

@csrf_exempt
def dashboard(request):
    try:
        context=dict()              
        if request.method == "GET":
            if "product" in request.GET:
                emotions = main_models.Emotion.objects.all()

                product_name = request.GET.get("product")
                model_name = request.GET.get("model_name", None)
                category_list = request.GET.getlist("category_list")

                # category instance
                select_categories = main_models.Category.objects.select_related("product").filter(Q(product__name=product_name)&Q(name__in=category_list)).order_by("id")

                # condition 설정
                condition={
                    "is_labeled": True,
                    "product__name": product_name,
                }

                if model_name is not None:
                    condition["model_name"]=model_name

                # 제품, 모델이름, 카테고리에 해당하는 리뷰를 가져옴(라벨링 작업이 끝난)
                review_by_condition = main_models.Review.objects.select_related("product").filter(**condition)

                # 리뷰에 대한 작업 데이터
                labeling_data = main_models.LabelingData.objects.select_related(
                    "review", "category", "emotion"
                    ).filter(Q(review__in=review_by_condition)&Q(category__in=select_categories))

                # emotion_rank_data 생성
                emotion_rank_data={}
                for emotion in emotions:
                    emotion_rank_data[emotion.e_name]={
                        "target": list(labeling_data.filter(emotion=emotion, target__isnull=False).values_list('target', flat=True).annotate(count=Count('target')).order_by('-count')[:10]),
                        "phenomenon": list(labeling_data.filter(emotion=emotion, phenomenon__isnull=False).values_list('phenomenon', flat=True).annotate(count=Count('phenomenon')).order_by('-count')[:10])
                    }

                # count_by_category 생성
                count_by_category = {}
                for select_category in select_categories:
                    count_by_category[select_category.name]={
                        "positive": labeling_data.filter(Q(category=select_category)&Q(emotion__e_name="positive")).count(),
                        "negative": labeling_data.filter(Q(category=select_category)&Q(emotion__e_name="negative")).count(),
                        "neutral": labeling_data.filter(Q(category=select_category)&Q(emotion__e_name="neutral")).count(),
                    }
                
                # total_by_review 생성
                total_by_review = {}
                for emotion in emotions:
                    total_by_review[emotion.e_name] = labeling_data.filter(emotion=emotion).count()

                # select_raw_data
                select_raw_data={}
                for select_category in select_categories:
                    select_raw_data[select_category.name]={
                        "positive": list((labeling_data.filter(Q(category=select_category)&Q(emotion__e_name="positive")).distinct()).values_list("review__content", flat=True)),
                        "negative": list((labeling_data.filter(Q(category=select_category)&Q(emotion__e_name="negative")).distinct()).values_list("review__content", flat=True))
                    }
                
                # response_data
                context["emotion_rank_data"] = emotion_rank_data
                context["raw_data"] = list(review_by_condition.values_list("content", flat=True))
                context["count_by_category"] = count_by_category
                context["total_by_review"] = total_by_review
                context["select_raw_data"] = select_raw_data

            elif "product" not in request.GET:
                qs_product = main_models.Product.objects.all()
                qs_review = main_models.Review.objects.all()
                qs_category = main_models.Category.objects.all()

                res_data={}
                for product in qs_product:
                    model_names_by_product = qs_review.filter(product=product).exclude(model_name="").values_list("model_name", flat=True).distinct()
                    categories_by_product = qs_category.filter(product=product).values_list("name", flat=True)
                    res_data[product.name] = {"model_name":list(model_names_by_product), "category":list(categories_by_product)}

                context["product"] = res_data
        return render(request, "dashboard/dashboard.html", context=context)

    # 예외처리
    except Exception as identifier:
        print(identifier)
    context = dict()
    return render(request, "dashboard/dashboard.html", context=context)

@csrf_exempt
def dashboard_by_date(request):
    try:
        context=dict()              
        if request.method == "GET":
            if "product_name" in request.GET:
                product_name = request.GET.get("product_name")
                model_name = request.GET.get("model_name", None)
                parsed_start_date = datetime.strptime(request.GET.get("start_date"), "%Y-%m-%d").date()
                parsed_end_date = datetime.strptime(request.GET.get("end_date"), "%Y-%m-%d").date()

                # category_by_product
                categories = main_models.Category.objects.filter(product__name=product_name)

                # 6등분한 날짜 계산
                divided_dates = calculate_date_intervals(parsed_start_date, parsed_end_date, 6)
        
                # condition 설정
                condition={
                    "review__product__name": product_name,
                    "review__date_writted__range": [parsed_start_date, parsed_end_date],
                }

                if model_name is not None:
                    condition["review__model_name"] = model_name

                # labeling_data_by_condition
                labeling_data = main_models.LabelingData.objects.select_related(
                    "review__product", "category"
                ).filter(**condition)

                # review_count_by_category
                review_count_by_category = {}
                for category in categories:
                    date_count_list = []
                    for divided_date in divided_dates:
                        date_count_list.append(
                            {
                                "date": f"{divided_date['start']} ~ {divided_date['end']}",
                                "count": labeling_data.filter(category=category, review__date_writted__range=[divided_date['start'], divided_date['end']]).values("review").distinct().count()
                            }
                        )
                    review_count_by_category[category.name]=date_count_list

                context["review_count_by_category"] = review_count_by_category

            elif "product_name" not in request.GET:
                qs_product = main_models.Product.objects.all()
                qs_review = main_models.Review.objects.all()

                res_data={}
                for product in qs_product:
                    model_names_by_product = qs_review.filter(product=product).exclude(model_name="").values_list("model_name", flat=True).distinct()
                    res_data[product.name] = {"model_name":list(model_names_by_product)}

                context["product"] = res_data
        return render(request, "dashboard/dashboard_date.html", context=context)

    # 예외처리
    except Exception as identifier:
        print(identifier)
    context = dict()
    return render(request, "dashboard/dashboard_date.html", context=context)