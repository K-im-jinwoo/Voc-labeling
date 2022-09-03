from datetime import datetime
from django.http import HttpResponse
import csv
from django.shortcuts import render

# Create your views here.
from django.urls import reverse

from mainapp.models import Category, Review, FirstLabeledData


def output(request):
    try:

        # category_product 변수를 get 방식 으로 받으면 세션에 저장
        if request.method == "GET":
            if 'category_product' in request.GET:
                request.session['category_product'] = request.GET['category_product']
                print(request.session['category_product'])
                request.session.set_expiry(300)

                category_product = request.session['category_product']
                category_detail = Category.objects.filter(category_product=category_product)
                alltotal = Review.objects.filter(category_product=category_product).count()
                first_num = Review.objects.filter(category_product=category_product).filter(first_status=True).count()
                second_num = Review.objects.filter(category_product=category_product).filter(second_status=True).count()
                dummy_num = Review.objects.filter(category_product=category_product).filter(dummy_status=True).count()

                context = {'category_detail': category_detail}
                context['alltotal'] = alltotal
                context['first_num'] = first_num
                context['dummy_num'] = dummy_num
                context['second_num'] = second_num
                return render(request, 'outputapp/output.html', context)

            else:
                context = {'message': '제품을 다시 선택해주세요.'}
                return render(request, 'outputapp/output.html', context)

        elif request.method == "POST" and 'export' in request.POST:
            if request.POST['export'] == '.csv export':

                ####---- HttpResponse 설정 ----####
                product = request.POST['product']
                response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = 'attachment; filename=' + product + '_' + datetime.now().strftime(
                    "%Y-%m-%d_%I-%M-%S_%p") + '.csv'
                response.write(u'\ufeff'.encode('utf8'))
                writer = csv.writer(response)


                """ 카테고리별 개수 저장 & 열 이름 지정 """
                ##### ---- 카테고리별 [긍정, 부정, 중립] 중 가장 많은 수 딕셔너리에 저장 ---- #####
                category_list = list(
                    Category.objects.filter(category_product=request.session['category_product']).values_list(
                        'category_id', flat=True))
                category_dict = {}
                for category in category_list:
                    max_count = 0
                    for emotion in ['positive', 'negative', 'neutral']:
                        emotion_count = len(FirstLabeledData.objects.filter(
                            category_id__category_product=request.session['category_product'], category_id=category,
                            first_labeled_emotion=emotion).values_list('first_labeled_target',
                                                                       'first_labeled_expression').distinct())
                        if emotion_count >= max_count:
                            max_count = emotion_count
                    if max_count == 0:
                        continue
                    category_dict[category] = max_count
                print(category_dict)

                ##### ---- 가장 많은 카테고리 기준으로 만들기 ---- #####
                max_count = max(list(category_dict.values()))
                all_keyword = [['']] * max_count

                ##### ---- 열 이름 지정하기 ---- #####
                row_names = ['', '카테고리', '긍정', '부정', '중립'] * len(list(category_dict.keys()))
                writer.writerow(row_names)


                """ 내용 입력 부분 """
                for category in list(category_dict.keys()):

                    ##### ---- 카테고리명 입력 ---- #####
                    category_name = Category.objects.get(category_id=category).category_middle
                    category_keyword = FirstLabeledData.objects.filter(category_id=category,
                                                                       category_id__category_product=request.session[
                                                                           'category_product'])
                    for i in range(category_dict[category]):
                        all_keyword[i] = all_keyword[i] + [category_name]
                    for i in range(category_dict[category], max_count):
                        all_keyword[i] = all_keyword[i] + ['']

                    ##### ---- 감정별 키워드 입력 ---- #####
                    for emotion in ['positive', 'negative', 'neutral']:
                        emotion_keyword = list(
                            category_keyword.filter(first_labeled_emotion=emotion).values_list('first_labeled_target',
                                                                                               'first_labeled_expression').distinct())
                        for i in range(len(emotion_keyword)):
                            all_keyword[i] = all_keyword[i] + [
                                list(emotion_keyword[i])[0] + 'AND' + list(emotion_keyword[i])[1]]
                        for i in range(len(emotion_keyword), max_count):
                            all_keyword[i] = all_keyword[i] + ['']

                    ##### ---- 한 칸 띄우기 ---- #####
                    for i in range(max_count):
                        all_keyword[i] = all_keyword[i] + ['']

                for rlt in all_keyword:
                    writer.writerow(rlt)

                return response

            elif request.POST['export'] == '.data analysis':

                ####---- HttpResponse 설정 ----####
                product = request.POST['product']
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename=' + product + '_' + datetime.now().strftime(
                    "%Y-%m-%d_%I-%M-%S_%p") + '.csv'
                response.write(u'\ufeff'.encode('utf8'))

                ####---- csv 파일 만들기 ----####
                writer = csv.writer(response)
                reviews = list(
                    Review.objects.filter(first_status=True, category_product=product).values_list('review_id',
                                                                                                   flat=True))
                review_contents = list(
                    Review.objects.filter(first_status=True, category_product=product).values_list('review_content',
                                                                                                   flat=True))
                result = [['']] * len(reviews)
                for i in range(len(reviews)):
                    categorys = FirstLabeledData.objects.filter(review_id=reviews[i],
                                                                category_id__category_product=product).values_list(
                        'category_id__category_middle', flat=True)
                    review_category = ''
                    for category in categorys:
                        review_category += category + 'and'
                    review_category = review_category[:-3]
                    result[i] = [reviews[i], review_contents[i], review_category]
                print(result[0])

                # 6. csv 파일 만들기
                writer.writerow(['리뷰 번호', '리뷰 원문', '카테고리'])
                for rlt in result:
                    writer.writerow(rlt)
                return response

            else:
                print("에러입니다.")

        else:
            print("에러")


    except Exception as identifier:
        print(identifier)
    return render(request, 'outputapp/output.html')
