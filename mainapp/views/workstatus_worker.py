from django.contrib.auth.models import User
from django.shortcuts import render

from mainapp.models import Category, Review

from django.http import JsonResponse



def workstatus_worker(request):
    temp_user = User.objects.all()
    # temp_user = User.objects.filter(is_superuser=False)
    result_name = []
    result_count = []
    context = {}
    if 'category_product' in request.GET:
        category_product = request.GET['category_product']
        for i in temp_user:
            temp_count = Review.objects.filter(category_product=category_product, labeled_user_id=int(i.pk)).count()
            result_name.append(i.username)
            result_count.append(temp_count)
        result = zip(result_name, result_count)
        result_list = list(result)
        
        context = {'result': result, 'category_product': category_product, 'result_list' : result_list}
        
    # product_names 가져오기
    
    product_names = Category.objects.all().values_list('category_product', flat=True).distinct()
    context['product_names'] = product_names
    return render(request, 'mainapp/workstatus_count.html', context=context)


def server(request):
    print("버튼 적용 성공")
    # 시간정해서 작업하지않은 리뷰 할당상태 변경하는 코드
    Review.objects.all().update(first_assign_user=0,second_assign_user=0)
    print("완료")

    return render(request, 'mainapp/workstatus_count.html')
