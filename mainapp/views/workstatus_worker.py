from django.contrib.auth.models import User
from django.shortcuts import render

from mainapp.models import Review


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
        context = {'result': result, 'category_product': category_product}

    return render(request, 'mainapp/workstatus_count.html', context=context)
