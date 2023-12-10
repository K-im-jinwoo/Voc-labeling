from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpResponseRedirect

from main import models as main_models


def make_webStatus():
    web_status = main_models.WebStatus()
    web_status.status_name = 'auto_assignment_value'
    web_status.status_value = str(0)
    web_status.save()

    web_status = main_models.WebStatus()
    web_status.status_name = 'auto_assignment_status'
    web_status.status_value = str(0)
    web_status.save()


def assignment(request):
    #### ---- staff만 작업 할당 가능함 ---- ####
    if request.user.is_staff == 0:
        return render(request, 'main/main_page.html')

    #### ---- 자동 할당 상태 data가 없으면 임시로 만듦 ---- ####
    if not main_models.WebStatus.objects.filter(status_name='auto_assignment_value').exists():
        make_webStatus()

    #### ---- 화면에 보낼 데이터 ---- ####
    context = dict()
    users = User.objects.all()
    categorys = main_models.Category.objects.all().values('category_product').distinct()
    context['users'] = users
    context['category_products'] = categorys
    context['auto_assignment_value'] = main_models.WebStatus.objects.get(status_name='auto_assignment_value').status_value
    context['auto_assignment_status'] = main_models.WebStatus.objects.get(status_name='auto_assignment_status').status_value

    #### ---- 유저별 작업 상태 할당하기 & 삭제하기 ---- ####
    if request.method == "POST" and 'assignment_status' in request.POST:
        category_product = request.POST.get('category_product')
        user = request.POST.get('assignment_user')
        assignment_status = request.POST.get('assignment_status')

        # 유저별 1000개씩 할당하기
        if assignment_status == 'assignment' and category_product != "all" and user != 'all':
            review = main_models.Review.objects.filter(category_product=category_product, first_status=0, second_status=0,
                                           dummy_status=0, first_assign_user=0).values('pk')[:1000]
            review = main_models.Review.objects.filter(pk__in=review)
            review.update(first_assign_user=user)
            return HttpResponseRedirect('/assignment/')

        # 유저별 할당 상태 삭제하기
        elif assignment_status == 'assignment_delete':
            review = main_models.Review.objects.filter(
                category_product__in=[category_product] if category_product != 'all' else categorys.values(
                    'category_product'), first_status=0, second_status=0,
                dummy_status=0, first_assign_user__in=[user] if user != 'all' else users).values('pk')
            review = main_models.Review.objects.filter(pk__in=review)
            review.update(first_assign_user=0)
            return HttpResponseRedirect('/assignment/')

    #### ---- 자동 할당 상태 활성화 or 비활성화 ---- ####
    if request.method == "POST" and 'auto_assignment_value' in request.POST:
        auto_assignment_value = request.POST.get('auto_assignment_value')
        auto_assignment_status = auto_assignment_value != "" and int(auto_assignment_value) > 0

        main_models.WebStatus.objects.filter(status_name='auto_assignment_value').update(status_value=auto_assignment_value)
        main_models.WebStatus.objects.filter(status_name='auto_assignment_status').update(status_value=auto_assignment_status)
        return HttpResponseRedirect('/assignment/')

    return render(request, 'main/assignment.html', context)
