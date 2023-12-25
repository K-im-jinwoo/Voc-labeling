from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import render

from main import models as main_models

def workstatus_worker(request):
    context = dict()
    # 제품군 리스트
    context["product_names"] = main_models.Product.objects.all().order_by("id")

    if "product" in request.GET:
        select_product = request.GET["product"]
        context["product"] = select_product

        # user
        user = main_models.Profile.objects.all().order_by("name")
        # 제품군에 해당하는 작업완료 된 review
        worked_review = main_models.Review.objects.filter(product__name=select_product, worked_user__isnull=False)

        worker_count_dict={}
        for user in user:
            user_review_count = worked_review.filter(worked_user=user).count()
            worker_count_dict[user.name]=user_review_count
        
        context["worker_count_dict"]=worker_count_dict
    return render(request, "main/workstatus_worker.html", context=context)


def server(request):
    print("버튼 적용 성공")
    # 시간정해서 작업하지않은 리뷰 할당상태 변경하는 코드
    main_models.Review.objects.all().update(first_assign_user=0, second_assign_user=0)
    print("완료")

    return render(request, "main/workstatus_worker.html")
