from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import render

from main import models as main_models

def workstatus_worker(request):
    temp_user = User.objects.all()
    # temp_user = User.objects.filter(is_superuser=False)
    result_name = []
    result_count = []
    context = {}

    if "category_product" in request.GET:
        category_product = request.GET["category_product"]
        for i in temp_user:
            temp_count = main_models.Review.objects.filter(
                category_product=category_product, labeled_user_id=int(i.pk)
            ).count()
            result_name.append(i.username)
            result_count.append(temp_count)
        result = zip(result_name, result_count)
        result_list = list(result)

        context = {
            "result": result,
            "category_product": category_product,
            "result_list": result_list,
        }

    # product_names 가져오기
    review_count = main_models.Review.objects.count()  # 총리뷰수
    context["review_count"] = review_count
    users_with_review_counts = User.objects.annotate(
        review_count=Count("review")
    )  # 아이디당 리뷰 몇개달았는
    context["users_with_review_counts"] = users_with_review_counts
    total_review_count_by_users = 0  # 아이디당 리뷰 수 총 합
    for user in users_with_review_counts:
        total_review_count_by_users += user.review_count
    context["total_review_count_by_users"] = total_review_count_by_users
    product_names = (
        main_models.Category.objects.all().values_list("category_product", flat=True).distinct()
    )
    context["product_names"] = product_names
    return render(request, "main/workstatus_worker.html", context=context)


def server(request):
    print("버튼 적용 성공")
    # 시간정해서 작업하지않은 리뷰 할당상태 변경하는 코드
    main_models.Review.objects.all().update(first_assign_user=0, second_assign_user=0)
    print("완료")

    return render(request, "main/workstatus_worker.html")
