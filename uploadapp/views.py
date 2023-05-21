# -*- coding: utf-8 -*-
from django.core.files.storage import FileSystemStorage
from django.db.models import Max
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
import pandas as pd

# Create your views here.
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView
from numpy.ma.core import count

from LG_Project.settings.base import BASE_DIR
from mainapp.models import Review, Category
from django.http import JsonResponse

from django.http import JsonResponse

from django.shortcuts import get_object_or_404, redirect

def delete_category(request):
    if request.method == 'POST':
        category_middle = request.POST.get('category_middle')
        category = Category.objects.filter(category_middle=category_middle)[0]
        category.delete()
        url = reverse('uploadapp:upload') + f'?category_product={category.category_product}'
    return HttpResponseRedirect(url)

def cleansing(csv_file):
    '''전처리 시작'''
    raw_data = pd.read_csv("." + csv_file, encoding='utf-8')
    print(raw_data)
    data = raw_data.filter(['Original Comments'])

    '''중복 제거(1)'''
    data = data.drop_duplicates(['Original Comments'])

    '''불필요한 문자열 제거'''
    # html태그 제거
    data['Original Comments'] = data['Original Comments'].str.replace(pat=r'<[^>]*>', repl=r'', regex=True)

    # email 주소 제거
    data['Original Comments'] = data['Original Comments'].str.replace(
        pat=r'(\[a-zA-Z0-9\_.+-\]+@\[a-zA-Z0-9-\]+.\[a-zA-Z0-9-.\]+)',
        repl=r'', regex=True)
    # _제거
    data['Original Comments'] = data['Original Comments'].str.replace('_', '')

    # \r, \n 제거
    data['Original Comments'] = data['Original Comments'].str.replace(pat=r'[\r|\n]', repl=r'', regex=True)

    # url 제거
    data['Original Comments'] = data['Original Comments'].str.replace(
        pat=r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''',
        repl=r'', regex=True)
    data['Original Comments'] = data['Original Comments'].str.replace(
        pat=r'((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*',
        repl=r'', regex=True)

    # 자음, 모음 제거
    data['Original Comments'] = data['Original Comments'].str.replace(pat=r'([ㄱ-ㅎㅏ-ㅣ]+)', repl=r'', regex=True)

    # 특수 기호 제거
    data['Original Comments'] = data['Original Comments'].str.replace(pat=r'[^\w\s]', repl=r'', regex=True)
    data['Original Comments'] = data['Original Comments'].str.replace('1n', '')
    data['Original Comments'] = data['Original Comments'].str.replace('_', '')

    # 모두 영어인 행 공백으로 대체
    data['Original Comments'] = data['Original Comments'].str.replace(pat=r'^[a-zA-Z\s]+$', repl=r'', regex=True)

    # 모두 숫자인 행 공백으로 대체
    data['Original Comments'] = data['Original Comments'].str.replace(pat=r'^[0-9\s]+$', repl=r'', regex=True)

    # 좌우 공백 제거
    data['Original Comments'] = data['Original Comments'].str.strip()

    # 아이디 관련 단어 제거
    data['Original Comments'] = data['Original Comments'].str.replace(pat=r'ID\s[a-zA-Z0-9]+', repl=r'',
                                                                    regex=True)
    data['Original Comments'] = data['Original Comments'].str.replace(pat=r'아이디\s[a-zA-Z0-9]+', repl=r'',
                                                                    regex=True)
    data['Original Comments'] = data['Original Comments'].str.replace(pat=r'id\s[a-zA-Z0-9]+', repl=r'',
                                                                    regex=True)
    data['Original Comments'] = data['Original Comments'].str.replace(pat=r'ID[a-zA-Z0-9]+', repl=r'', regex=True)
    data['Original Comments'] = data['Original Comments'].str.replace(pat=r'아이디[a-zA-Z0-9]+', repl=r'',
                                                                    regex=True)
    data['Original Comments'] = data['Original Comments'].str.replace(pat=r'id[a-zA-Z0-9]+', repl=r'', regex=True)
    data['Original Comments'] = data['Original Comments'].str.replace(pat=r'ID\s', repl=r'', regex=True)
    data['Original Comments'] = data['Original Comments'].str.replace(pat=r'아이디\s', repl=r'', regex=True)
    data['Original Comments'] = data['Original Comments'].str.replace(pat=r'id\s', repl=r'', regex=True)

    # 주문번호 관련 단어 제거
    data['Original Comments'] = data['Original Comments'].str.replace(pat=r'주문번호\s[a-zA-Z0-9]+', repl=r'',
                                                                    regex=True)
    data['Original Comments'] = data['Original Comments'].str.replace(pat=r'결제번호\s[a-zA-Z0-9]+', repl=r'',
                                                                    regex=True)
    data['Original Comments'] = data['Original Comments'].str.replace(pat=r'구매번호\s[a-zA-Z0-9]+', repl=r'',
                                                                    regex=True)
    data['Original Comments'] = data['Original Comments'].str.replace(pat=r'주문\s번호\s[a-zA-Z0-9]+', repl=r'',
                                                                    regex=True)
    data['Original Comments'] = data['Original Comments'].str.replace(pat=r'결제\s번호\s[a-zA-Z0-9]+', repl=r'',
                                                                    regex=True)
    data['Original Comments'] = data['Original Comments'].str.replace(pat=r'구매\s번호\s[a-zA-Z0-9]+', repl=r'',
                                                                    regex=True)
    data['Original Comments'] = data['Original Comments'].str.replace(pat=r'주문번호\s', repl=r'', regex=True)
    data['Original Comments'] = data['Original Comments'].str.replace(pat=r'결제번호\s', repl=r'', regex=True)
    data['Original Comments'] = data['Original Comments'].str.replace(pat=r'구매번호\s', repl=r'', regex=True)
    data['Original Comments'] = data['Original Comments'].str.replace(pat=r'주문\s번호\s', repl=r'', regex=True)
    data['Original Comments'] = data['Original Comments'].str.replace(pat=r'결제\s번호\s', repl=r'', regex=True)
    data['Original Comments'] = data['Original Comments'].str.replace(pat=r'구매\s번호\s', repl=r'', regex=True)

    '''중복 제거(2)'''
    data['temp'] = data['Original Comments']
    data['temp'] = data['temp'].str.replace(' ', '')
    data = data.drop_duplicates(['temp'], ignore_index=True)
    data = data.drop(['temp'], axis=1)
    print(data)
    return data


def upload_main(request):
    try:
        if request.method == "GET":
            context = dict()
            context['product_names'] = Category.objects.all().values('category_product').distinct()
            request.session['category_product'] = '--제품을 선택하세요--'
            if request.GET.get('category_product'):
                request.session['category_product'] = request.GET.get('category_product')
            context['category_detail'] = Category.objects.filter(category_product=request.session['category_product'])
            category_product = request.POST.get('category_product')
            return render(request, 'uploadapp/upload_main.html', context)

        elif request.method == "POST":
            if request.POST.get('category_add'):
                category = Category()
                category.category_product = request.POST.get('category_add')
                category.category_middle = '기타'
                category.category_color = '#c8c8c850'
                category.save()
                return HttpResponseRedirect(reverse('uploadapp:upload'))
            
            if request.POST.get('category_update'):
                category_product = request.POST.get('category_product')
                category_update = request.POST.get('category_update')
                category = Category.objects.get(category_product=category_product)
                category.category_product = category_update
                category.save()

                return HttpResponseRedirect(reverse('uploadapp:upload'))

            if request.POST.get("form-type") == 'formOne':
                category = Category()
                category.category_product = request.session['category_product']
                category.category_middle = request.POST.get('category_middle', '')
                temp_color = str(request.POST.get('category_color', '')) + "50"
                category.category_color = temp_color
                category.save()
                category_product = request.GET.get('category_product')
                url = reverse('uploadapp:upload') + f'?category_product={category.category_product}'
                return HttpResponseRedirect(url)

            if request.POST.get('session_product'):
                print("제품삭제 뷰")
                session_product = request.POST.get('session_product')
                print(session_product)
                product_review = Review.objects.filter(category_product=session_product).delete()
                product_category = Category.objects.filter(category_product=session_product).delete()
                print(product_category)
                return HttpResponseRedirect(reverse('uploadapp:upload'))

            elif request.POST.get("form-type") == 'formTwo':
                # upload_files 변수에 파일 저장시 Review 모델에 저장
                if request.FILES['upload_file']:

                    # csv 형식으로 저장
                    upload_file = request.FILES['upload_file']
                    if not upload_file.name.endswith('csv'):
                        request.session['message'] = '<<Error>> 엑셀 형식으로 업로드 해주세요'
                        request.session.set_expiry(3)
                        return HttpResponseRedirect(reverse('uploadapp:upload'))

                    # 데이터 전처리 및 정제 작업
                    fs = FileSystemStorage()
                    filename = fs.save(upload_file.name, upload_file)
                    upload_file_url = fs.url(filename)
                    dbframe = cleansing(upload_file_url)
                    fs.delete(str(BASE_DIR) + upload_file_url)

                    # 중복 제거하기
                    dbreviews = Review.objects.filter(
                        category_product=request.POST.get('category_product')).values_list('review_content', flat=True)
                    dbreviews = pd.DataFrame({"Original Comments": dbreviews})

                    dbframe = pd.merge(dbreviews, dbframe, how='outer', indicator=True).query(
                        '_merge == "right_only"').drop(columns=['_merge'])
                    print(dbframe)
                    # 현재 model의 category_product별로 최대값을 기준으로 review_number을 갱신하기 위한 변수 category_max_num
                    category_max_num = Review.objects.filter(
                        category_product=request.POST.get('category_product')).aggregate(temp=Max('review_number')).get(
                        'temp', None)
                    if category_max_num == None:
                        category_max_num = 0
                    dbframe.reset_index(inplace=True)
                    dbframe['index'] = dbframe['index'] + int(category_max_num) + 1

                    # 저장 부분
                    review_obj = [Review(review_content=row['Original Comments'],
                    category_product=request.POST.get('category_product'),
                    review_number=row['index']) for _, row in dbframe.iterrows()]
                    Review.objects.bulk_create(review_obj)
                    request.session['message'] = '업로드가 완료되었습니다.'
                    request.session.set_expiry(3)
                    url = reverse('uploadapp:upload') + f'?category_product={request.POST.get("category_product")}'
                    return HttpResponseRedirect(url)

        return render(request, 'uploadapp/upload_main.html', {})

    # 예외 처리
    except Exception as identifier:
        print(identifier)

    return render(request, 'uploadapp/upload_main.html', {})