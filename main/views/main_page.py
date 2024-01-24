from django.contrib.auth.models import User
from django.db.models import Count, Q, Sum
from django.shortcuts import render
from main import models as main_models

def main_page(request):
    context = {}

    # 제품별 모델 개수 가져오기
    product_names = main_models.Review.objects.values("product__name").distinct()
    product_model_counts = []
    for product in product_names:
        model_name_count = (
            main_models.Review.objects.exclude(Q(model_name__isnull=True) | Q(model_name=""))
            .filter(product__name=product["product__name"])
            .values("model_name")
            .distinct()
            .count()
        )
        product_model_counts.append({
            "category_product": product["product__name"],
            "model_name_count": model_name_count,
        })

    context["product_model_counts"] = sorted(product_model_counts, key=lambda x: x["category_product"])[:5]

    # 제품별 리뷰 총 개수 및 레이블링된 개수 계산
    category_review_counts = main_models.Review.objects.values("product__name").annotate(
        review_count=Count("content")
    )
    category_review_counts_labeled = (
        main_models.Review.objects.filter(worked_user__isnull=False)
        .values("product__name")
        .annotate(labeled_count=Count("content"))
    )

    result_list = []
    for item in category_review_counts:
        matched_item = next(
            (x for x in category_review_counts_labeled if x["product__name"] == item["product__name"]),
            None,
        )
        labeled_count = matched_item["labeled_count"] if matched_item else 0
        percentage_labeled = round((labeled_count / item["review_count"]) * 100) if item["review_count"] > 0 else 0

        result_list.append({
            "category_product": item["product__name"],
            "total_reviews": item["review_count"],
            "labeled_count": labeled_count,
            "percentage_labeled": percentage_labeled,
        })

    context["result"] = sorted(result_list, key=lambda x: x["category_product"])[:5]

    # 기본 정보: 제품 수, 유저 수, 리뷰 수
    product_count = main_models.Category.objects.values("product__name").distinct().count()
    user_count = User.objects.count()
    review_count = main_models.Review.objects.count()

    context["product_count"] = product_count
    context["user_count"] = user_count
    context["review_count"] = review_count

    # 리뷰 비율 계산
    total_review_count = main_models.Review.objects.all().count()
    labeled_reviews_count = main_models.Review.objects.filter(is_labeled=True).count()
    if total_review_count != 0 and labeled_reviews_count != 0:
        ratio = round(labeled_reviews_count / total_review_count * 100, 1)
        print(total_review_count)
        print(labeled_reviews_count)
        context["review_ratio"] = ratio
    else:
        context["review_ratio"] = 0

    # 유저별 리뷰 개수 및 비율    
    result_list = []
    # 전체 리뷰 수
    total_review_count = main_models.Review.objects.all().count()
    user_name_list = User.objects.all()
    for user_name in user_name_list:
        user_labeled_count = main_models.Review.objects.filter(worked_user__user__username=user_name).count()
        user_ratio_percentage = 0
        if total_review_count != 0:
            user_ratio_percentage = int((user_labeled_count / total_review_count) * 100)
        result_list.append((user_name, user_labeled_count, user_ratio_percentage))
    result_list = sorted(result_list, key=lambda x: x[1], reverse=True)
    context["result_list"] = result_list

    return render(request, "main/main_page.html", context)