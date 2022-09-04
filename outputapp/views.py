from datetime import datetime
from io import BytesIO

import pandas as pd
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
                all_keywords = FirstLabeledData.objects.filter(category_id__category_product=request.POST['product'])
                categorys = Category.objects.filter(category_product=request.POST['product']).values_list(
                    'category_middle', flat=True)
                with BytesIO() as b:
                    writer = pd.ExcelWriter(b, engine='xlsxwriter')
                    for category in categorys:
                        keywords = {'positive_keyword':'', 'negative_keyword':'', 'neutral_keyword':''}
                        counts = {}
                        for emotion in ['positive', 'negative', 'neutral']:
                                temp_keyword = list(all_keywords.filter(category_id__category_middle=category,
                                                                        first_labeled_emotion=emotion).values_list(
                                    'first_labeled_target', 'first_labeled_expression').distinct())
                                for i in range(len(temp_keyword)):
                                    temp_keyword[i] = list(temp_keyword[i])[0] + ' AND ' + list(temp_keyword[i])[1]

                                counts[emotion + '_keyword'] = len(temp_keyword)
                                keywords[emotion + '_keyword'] = temp_keyword
                                product_group = [request.POST['product']] * max(counts.values())
                                type_ = ['3F_Ergonomics'] * max(counts.values())
                                category_list = [category] * max(counts.values())
                                dict_ = {'Product_Group': product_group,
                                              'Type': type_, 'Category': category_list, '긍정 키워드':keywords['positive_keyword'], '부정 키워드':keywords['negative_keyword'], '중립 키워드':keywords['neutral_keyword']}
                                df = pd.DataFrame.from_dict(dict_, orient='index')
                                df = df.transpose()

                                df.to_excel(writer, sheet_name=category)
                    writer.save()
                    filename = request.POST['product']
                    content_type = 'application/vnd.ms-excel'
                    response = HttpResponse(b.getvalue(), content_type=content_type)
                    response['Content-Disposition'] = 'attachment; filename="' + filename + '.xlsx"'
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
