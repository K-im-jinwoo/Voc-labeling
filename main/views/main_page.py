from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.shortcuts import render

from main import models as main_models

def main_page(request):
    context = dict()
    # 제품별 모델개수
    product_names = main_models.Review.objects.values("category_product").distinct()
    product_model_counts = []
    for product in product_names:
        model_name_count = (
            main_models.Review.objects.exclude(Q(model_name__isnull=True) | Q(model_name=""))
            .filter(category_product=product["category_product"])
            .values("model_name")
            .distinct()
            .count()
        )
        product_model_counts.append(
            {
                "category_product": product["category_product"],
                "model_name_count": model_name_count,
            }
        )

    sorted_products = sorted(product_model_counts, key=lambda x: x["category_product"])
    context["product_model_counts"] = sorted_products[:5]

    # 제품별 리뷰 총 개수
    category_review_counts = main_models.Review.objects.values("category_product").annotate(
        review_count=Count("review_content")
    )
    category_review_counts_labeled = (
        main_models.Review.objects.filter(labeled_user_id__isnull=False)
        .values("category_product")
        .annotate(labeled_count=Count("review_content"))
    )

    result_list = []

    for item in category_review_counts:
        matched_item = next(
            (
                x
                for x in category_review_counts_labeled
                if x["category_product"] == item["category_product"]
            ),
            None,
        )
        labeled_count = matched_item["labeled_count"] if matched_item else 0
        percentage_labeled = (
            round((labeled_count / item["review_count"]) * 100)
            if item["review_count"] > 0
            else 0
        )

        result_list.append(
            {
                "category_product": item["category_product"],
                "total_reviews": item["review_count"],
                "labeled_count": labeled_count,
                "percentage_labeled": percentage_labeled,
            }
        )

    sorted_result_list = sorted(result_list, key=lambda x: x["category_product"])
    context["result"] = sorted_result_list[:5]

    # 메인 첫번째
    temp_user = User.objects.all()
    # temp_user = User.objects.filter(is_superuser=False)
    result_name = []
    result_count = []
    product_count = (
        main_models.Category.objects.values("category_product").distinct().count()
    )  # 제품갯수
    user_count = temp_user.count()  # 유저수
    review_count = main_models.Review.objects.count()  # 총리뷰수

    context["product_count"] = product_count
    context["user_count"] = user_count
    context["review_count"] = review_count

    users_with_review_counts = User.objects.annotate(
        review_count=Count("review")
    )  # 아이디당 리뷰 몇개달았는지 수

    total_review_count_by_users = 0  # 아이디당 리뷰 수 총 합
    for user in users_with_review_counts:
        total_review_count_by_users += user.review_count
        
    # user_ratio = int((total_review_count_by_users / review_count) * 100)
    # context["review_ratio"] = round(
    #     (total_review_count_by_users / review_count) * 100, 1
    # )  # 아이디당 리뷰 수 총합 / 총리뷰수
    if review_count != 0:
        context["review_ratio"] = round(
            (total_review_count_by_users / review_count) * 100, 1
        )
    else:
        # review_count가 0인 경우에 대한 처리
        context["review_ratio"] = 0

    # 메인 세번째
    user_name = []
    user_result_count = []
    user_ratios = []

    for user in users_with_review_counts:
        user_name.append(user.username)
        user_result_count.append(user.review_count)
        # user_ratio_percentage = int((user.review_count / review_count) * 100)
        if review_count != 0:
            user_ratio_percentage = int((user.review_count / review_count) * 100)
        else:
            # review_count가 0인 경우에 대한 처리
            user_ratio_percentage = 0
        user_ratios.append(user_ratio_percentage)
        result = zip(user_name, user_result_count, user_ratios)

    result = sorted(result, key=lambda x: x[1], reverse=True)
    context["result_list"] = result

    return render(request, "main/main_page.html", context)
