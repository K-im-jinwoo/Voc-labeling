from django.db.models import Q, Count
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from main import models as main_models

@csrf_exempt
def dashboard(request):
    try:
        context=dict()              
        if request.method == "GET":
            if "product" in request.GET:
                emotions = main_models.Emotion.objects.all()

                product_name = request.GET.get("product")
                model_name = request.GET.get("model_name")
                category_list = request.GET.getlist("category_list")

                # category instance
                select_categories = main_models.Category.objects.filter(Q(product__name=product_name)&Q(name__in=category_list))

                # condition 설정
                condition={
                    "is_labeled": True,
                    "product__name": product_name,
                }

                if model_name is not None:
                    condition["model_name"]=model_name

                # 제품, 모델이름, 카테고리에 해당하는 리뷰를 가져옴(라벨링 작업이 끝난)
                review_by_condition = main_models.Review.objects.filter(**condition)

                # 리뷰에 대한 작업 데이터
                labeling_data = main_models.LabelingData.objects.filter(Q(review__in=review_by_condition)&Q(category__in=select_categories))

                # emotion_rank_data 생성
                emotion_rank_data={}
                for emotion in emotions:
                    labeling_data_by_emotion = labeling_data.filter(emotion=emotion)
                    emotion_rank_data[emotion.e_name]={
                        "target": list(labeling_data_by_emotion.exclude(target=None).values_list('target', flat=True).annotate(count=Count('target')).order_by('-count')[:10]),
                        "phenomenon": list(labeling_data_by_emotion.exclude(phenomenon=None).values_list('phenomenon', flat=True).annotate(count=Count('phenomenon')).order_by('-count')[:10])
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
                
                # response_data
                context["emotion_rank_data"] = emotion_rank_data
                context["raw_data"] = list(review_by_condition.values_list("content", flat=True))
                context["count_by_category"] = count_by_category
                context["total_by_review"] = total_by_review

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
                print(context["product"])
        return render( request, "dashboard/dashboard.html", context=context)

    # 예외처리
    except Exception as identifier:
        print(identifier)
    context = dict()
    return render(request, "dashboard/dashboard.html", context=context)
