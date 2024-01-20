from django.contrib.auth.models import User
from django.shortcuts import render
from main import models as main_models
from django.http import JsonResponse

def workstatus_worker(request):
    context = dict()
    if request.method == "GET":
        # 프론트에서 넘겨줘야할 데이터: 제품
        product_name = request.GET.get("product")
        users = main_models.User.objects.all()

        user_count_list = []
        review_obj = main_models.Review.objects.all()
        for user in users:
            work_count = review_obj.filter(worked_user__user=user, product__name=product_name).count()
            work_count_dict = {user.username: work_count}
            user_count_list.append(work_count_dict)
        # 백에서 프론트로 넘겨줄 작업자별 작업 개수 데이터
        # [
        #     {
        #         "사용자 id": 작업 개수(int)
        #     },
        #     {
        #         "사용자 id": 작업 개수(int)
        #     },
        #     ...
        # ]
        print(user_count_list)
        return JsonResponse({"user_count_list": user_count_list})

    elif "product" not in request.GET:
        qs_product = main_models.Product.objects.all()
        context["product"] = qs_product

    return render(request, "main/workstatus_review.html", context=context)