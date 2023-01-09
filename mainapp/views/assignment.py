from django.shortcuts import render

from mainapp.models import Review


def assignment(request):
    if request.method == "POST" and request.POST.get('assignment'):
        category_product = '밥솥' # 임시 값
        review = Review.objects.filter(category_product=category_product, first_status=0, second_status=0, dummy_status=0, first_assign_user=0).values('pk')[:5]
        review = Review.objects.filter(pk__in=review)
        review.update(first_assign_user=request.user.pk if request.user.pk != None else "0")

    context = dict()
    return render(request, 'mainapp/assignment.html', context)


'''def print_review(assignment_num, category_product):
    # start,end와 같은 번호로 영역대 지정이 아닌 50개,100개들의 데이터 개수로 영역대 지정
    # '다음','버리기'시 리스트 변동 없게 해야함
    # 개수 지정하고 적용시켰을때 그 개수만큼 리스트에 들어오지만, '다음','버리기' 눌렀을 때, 리스트 마지막 숫자도
    # +1돼서 계속 무한으로 +1씩 늘어나는 상황 => 할당량 10개만 하고싶은데 새로운 10개씩 리스트 반복 생성(문제 해결해야 함)
    # 이후 할당 상태와 할당받은 사람 사용 예정
    print_review_list = Review.objects.filter(category_product=category_product,
                                              first_status=False, second_status=False, dummy_status=False,
                                              first_assignment=False, second_assignment=False).order_by('review_id')[:assignment_num]

    print("리스트",print_review_list)
    return print_review_list[:1]'''