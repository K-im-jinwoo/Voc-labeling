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
            if request.POST['export'] == '.xlsx export':

                ####---- HttpResponse 설정 ----####
                product = request.POST['product']
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename=' + product + '_' + datetime.now().strftime(
                    "%Y-%m-%d_%I-%M-%S_%p") + '.csv'
                response.write(u'\ufeff'.encode('utf8'))

                ####---- csv 파일 만들기 ----####
                writer = csv.writer(response)
                temp_keyword = list(FirstLabeledData.objects.filter(category_id__category_product=request.session['category_product']).values_list('category_id__category_middle', 'first_labeled_emotion', 'first_labeled_target', 'first_labeled_expression').distinct())
                all_keyword = [['']] * len(temp_keyword)

                ####---- 전체 키워드 뽑아오기 ----####
                row_names = ['카테고리', '감정', '키워드']
                for i in range(len(temp_keyword)):
                    all_keyword[i] = [list(temp_keyword[i])[0], list(temp_keyword[i])[1], list(temp_keyword[i])[2] + 'and' + list(temp_keyword[i])[3]]

                # 1. 카테고리 목록 만들기
                category_list = [list(
                    Category.objects.filter(category_product=request.session['category_product']).values_list(
                        'category_id', flat=True))]
                for i in category_list[0]:
                    category_list += [[int(i)]]
                print(category_list)

                # 2. 감정 목록 만들기
                emotion_list = [list(FirstLabeledData.objects.filter(
                    category_id__category_product=request.session['category_product']).values_list(
                    'first_labeled_emotion', flat=True).distinct())]
                for i in emotion_list[0]:
                    emotion_list += [[i]]

                for category in category_list:
                    category_keyword = FirstLabeledData.objects.filter(
                        category_id__category_product=request.session['category_product'], category_id__in=category)

                    # 3. 한 칸 띄워주기
                    row_names += ['']
                    for i in range(len(all_keyword)):
                        all_keyword[i] = all_keyword[i] + ['']

                    for emotion in emotion_list:

                        # 4. 열 이름 지정해주기
                        if category == category_list[0]:
                            category_name = '전체'
                        else:
                            category_name = str(
                                Category.objects.filter(category_id__in=category).values_list('category_middle', flat=True)[
                                    0])
                        if emotion == emotion_list[0]:
                            emotion_name = 'all'
                        else:
                            emotion_name = emotion[0]
                        row_names += [category_name + '_' + emotion_name]

                        # 5. 값 입력하기
                        emotion_keyword = list(category_keyword.filter(first_labeled_emotion__in=emotion).values_list(
                            'first_labeled_target', 'first_labeled_expression').distinct())
                        print(category_name, emotion, len(emotion_keyword))

                        for i in range(len(emotion_keyword)):
                            all_keyword[i] = all_keyword[i] + [list(emotion_keyword[i])[0] + 'and' + list(emotion_keyword[i])[1]]
                        for i in range(len(emotion_keyword), len(all_keyword)):
                            all_keyword[i] = all_keyword[i] + ['']

                # 6. csv 파일 만들기
                writer.writerow(row_names)
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
                reviews = list(Review.objects.filter(first_status=True, category_product=product).values_list('review_id', flat=True))
                review_contents = list(Review.objects.filter(first_status=True, category_product=product).values_list('review_content', flat=True))
                result = [['']] * len(reviews)
                for i in range(len(reviews)):
                    categorys = FirstLabeledData.objects.filter(review_id=reviews[i], category_id__category_product=product).values_list('category_id__category_middle', flat=True)
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
