from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
import pandas as pd

# Create your views here.
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView
from numpy.ma.core import count

from mainapp.models import Review, Category


def cleansing(csv_file):
    '''전처리 시작'''
    raw_data = pd.read_csv("." + csv_file, encoding='utf-8')
    print(raw_data)
    data = raw_data.filter(['Original Comment'])

    '''중복 제거(1)'''
    data = data.drop_duplicates(['Original Comment'])

    '''불필요한 문자열 제거'''
    # html태그 제거
    data['Original Comment'] = data['Original Comment'].str.replace(pat=r'<[^>]*>', repl=r'', regex=True)

    # email 주소 제거
    data['Original Comment'] = data['Original Comment'].str.replace(
        pat=r'(\[a-zA-Z0-9\_.+-\]+@\[a-zA-Z0-9-\]+.\[a-zA-Z0-9-.\]+)',
        repl=r'', regex=True)
    # _제거
    data['Original Comment'] = data['Original Comment'].str.replace('_', '')

    # \r, \n 제거
    data['Original Comment'] = data['Original Comment'].str.replace(pat=r'[\r|\n]', repl=r'', regex=True)

    # url 제거
    data['Original Comment'] = data['Original Comment'].str.replace(
        pat=r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''',
        repl=r'', regex=True)
    data['Original Comment'] = data['Original Comment'].str.replace(
        pat=r'((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*',
        repl=r'', regex=True)

    # 자음, 모음 제거
    data['Original Comment'] = data['Original Comment'].str.replace(pat=r'([ㄱ-ㅎㅏ-ㅣ]+)', repl=r'', regex=True)

    # 특수 기호 제거
    data['Original Comment'] = data['Original Comment'].str.replace(pat=r'[^\w\s]', repl=r'', regex=True)
    data['Original Comment'] = data['Original Comment'].str.replace('1n', '')
    data['Original Comment'] = data['Original Comment'].str.replace('_', '')

    # 모두 영어인 행 공백으로 대체
    data['Original Comment'] = data['Original Comment'].str.replace(pat=r'^[a-zA-Z\s]+$', repl=r'', regex=True)

    # 모두 숫자인 행 공백으로 대체
    data['Original Comment'] = data['Original Comment'].str.replace(pat=r'^[0-9\s]+$', repl=r'', regex=True)

    # 좌우 공백 제거
    data['Original Comment'] = data['Original Comment'].str.strip()

    # 아이디 관련 단어 제거
    data['Original Comment'] = data['Original Comment'].str.replace(pat=r'ID\s[a-zA-Z0-9]+', repl=r'',
                                                                    regex=True)
    data['Original Comment'] = data['Original Comment'].str.replace(pat=r'아이디\s[a-zA-Z0-9]+', repl=r'',
                                                                    regex=True)
    data['Original Comment'] = data['Original Comment'].str.replace(pat=r'id\s[a-zA-Z0-9]+', repl=r'',
                                                                    regex=True)
    data['Original Comment'] = data['Original Comment'].str.replace(pat=r'ID[a-zA-Z0-9]+', repl=r'', regex=True)
    data['Original Comment'] = data['Original Comment'].str.replace(pat=r'아이디[a-zA-Z0-9]+', repl=r'',
                                                                    regex=True)
    data['Original Comment'] = data['Original Comment'].str.replace(pat=r'id[a-zA-Z0-9]+', repl=r'', regex=True)
    data['Original Comment'] = data['Original Comment'].str.replace(pat=r'ID\s', repl=r'', regex=True)
    data['Original Comment'] = data['Original Comment'].str.replace(pat=r'아이디\s', repl=r'', regex=True)
    data['Original Comment'] = data['Original Comment'].str.replace(pat=r'id\s', repl=r'', regex=True)

    # 주문번호 관련 단어 제거
    data['Original Comment'] = data['Original Comment'].str.replace(pat=r'주문번호\s[a-zA-Z0-9]+', repl=r'',
                                                                    regex=True)
    data['Original Comment'] = data['Original Comment'].str.replace(pat=r'결제번호\s[a-zA-Z0-9]+', repl=r'',
                                                                    regex=True)
    data['Original Comment'] = data['Original Comment'].str.replace(pat=r'구매번호\s[a-zA-Z0-9]+', repl=r'',
                                                                    regex=True)
    data['Original Comment'] = data['Original Comment'].str.replace(pat=r'주문\s번호\s[a-zA-Z0-9]+', repl=r'',
                                                                    regex=True)
    data['Original Comment'] = data['Original Comment'].str.replace(pat=r'결제\s번호\s[a-zA-Z0-9]+', repl=r'',
                                                                    regex=True)
    data['Original Comment'] = data['Original Comment'].str.replace(pat=r'구매\s번호\s[a-zA-Z0-9]+', repl=r'',
                                                                    regex=True)
    data['Original Comment'] = data['Original Comment'].str.replace(pat=r'주문번호\s', repl=r'', regex=True)
    data['Original Comment'] = data['Original Comment'].str.replace(pat=r'결제번호\s', repl=r'', regex=True)
    data['Original Comment'] = data['Original Comment'].str.replace(pat=r'구매번호\s', repl=r'', regex=True)
    data['Original Comment'] = data['Original Comment'].str.replace(pat=r'주문\s번호\s', repl=r'', regex=True)
    data['Original Comment'] = data['Original Comment'].str.replace(pat=r'결제\s번호\s', repl=r'', regex=True)
    data['Original Comment'] = data['Original Comment'].str.replace(pat=r'구매\s번호\s', repl=r'', regex=True)

    '''중복 제거(2)'''
    data['temp'] = data['Original Comment']
    data['temp'] = data['temp'].str.replace(' ', '')
    data = data.drop_duplicates(['temp'], ignore_index=True)
    data = data.drop(['temp'], axis=1)
    print(data)
    return data


def upload_main(request):
    try:

        # category_product 변수를 get 방식 으로 받으면 세션에 저장
        if request.method == "GET":
            if 'category_product' in request.GET:
                request.session['category_product'] = request.GET['category_product']
                print(request.session['category_product'])
                request.session.set_expiry(300)

                category_product = request.session['category_product']
                category_detail = Category.objects.filter(category_product=category_product)
                context = {'category_detail': category_detail}
                return render(request, 'uploadapp/upload_main.html', context)

            else:
                category_product = request.session['category_product']
                category_detail = Category.objects.filter(category_product = category_product)
                context = {'category_detail': category_detail}
                return render(request, 'uploadapp/upload_main.html', context)

        elif request.method == "POST":
            if request.POST.get("form-type") == 'formOne':
                category = Category()
                category.category_product = request.session['category_product']
                print(request.session['category_product'])
                category.category_middle = request.POST.get('category_middle', '')
                temp_color = str(request.POST.get('category_color', '')) + "50"
                category.category_color = temp_color
                category.save()
                print(category)
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

                    # 현재 model의 category_product별로 최대값을 기준으로 review_number을 갱신하기 위한 변수 i
                    temp = Review.objects.filter(category_product=request.POST.get('category_product'))
                    i = count(temp)

                    # 데이터 하나씩 반복문 돌리기
                    for index, row in dbframe.iterrows():

                        # 데이터를 입력하는 category에 중복된 데이터가 있는지 검사
                        if Review.objects.filter(category_product=request.POST.get('category_product'),
                                                 review_content=row['Original Comment']).exists():
                            pass

                        # 데이터를 입력하는 category에 중복된 데이터가 없을 시 실행
                        else:
                            i += 1
                            status = str(int(int(index) / int(dbframe.shape[0]) * 100)) + '%'
                            print(status)
                            print(i)
                            obj = Review.objects.create(review_content=row['Original Comment'],
                                                        category_product=request.POST.get('category_product'),
                                                        review_number=i)
                            obj.save()

                    request.session['message'] = '업로드가 완료되었습니다.'
                    request.session.set_expiry(3)
                    return HttpResponseRedirect(reverse('uploadapp:upload'))

    # 예외 처리
    except Exception as identifier:
        print(identifier)

    return render(request, 'uploadapp/upload_main.html', {})