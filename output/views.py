from datetime import datetime
from io import BytesIO
import pandas as pd
from django.http import HttpResponse
import csv
from django.shortcuts import render
import urllib.parse

from main import models as main_models


def format_change(writer, category):
    writer.sheets[category.name].set_column("A:B", 15)  # Product_Group, Type 컬럼 넓이 변경
    writer.sheets[category.name].set_column("C:C", 10)  # Category 컬럼 넓이 변경
    writer.sheets[category.name].set_column("D:F", 35)  # 키워드 컬럼 넓이 변경

# 제품 선택에 대한 데이터
def data_by_select_product(select_product):
    # review_by_product(제품에 해당하는 리뷰 전체를 가져옴)
    review_by_product = main_models.Review.objects.filter(product__name=select_product)

    # all_total(제품에 해당하는 전체 review 개수)
    all_total = review_by_product.count()

    # labeled_num(작업 완료 상태 데이터 수)
    labeled_num = review_by_product.filter(is_labeled=True).count()

    # trashed_num(삭제 완료 데이터 수)
    trashed_num = review_by_product.filter(is_trashed=True).count()
    res_data={
        "all_total": all_total,
        "labeled_num": labeled_num,
        "trashed_num": trashed_num
    }
    return res_data


def output(request):
    try:
        context = dict()
        context["product_names"] = main_models.Product.objects.all().order_by("id")

        # category_product 변수를 get 방식으로 받으면 세션에 저장
        if request.method == "GET":
            if "product" in request.GET:
                select_product = request.GET["product"]

                # 선택된 제품군에 대한 데이터를 가져오는 함수
                res_data=data_by_select_product(select_product)
                # response
                context["select_product"] = select_product
                context["all_total"] = res_data["all_total"]
                context["labeled_num"] = res_data["labeled_num"]
                context["trashed_num"] = res_data["trashed_num"]

                # response 데이터 구조(일부러 주석처리 -> 프론트에서 사용하기 쉽게 response 내용 작성한 것)
                # {
                #     "product_names": "모든 제품군 리스트",
                #     "select_product" : "유저가 선택한 제품",
                #     "all_total" : "선택한 제품군의 모든 review데이터 수",
                #     "labeled_num" : "모든 review데이터 중 작업이 완료된 데이터 수",
                #     "trashed_num" : "모든 review데이터 중 버려진 데이터 수"
                # }
            return render(request, "output/output.html", context)


        elif request.method == "POST" and "export" in request.POST:
            select_product=request.POST["product"]
            if request.POST["export"] == ".xlsx export":
                # 선택한 제품의 작업된 데이터를 가져옴
                labeled_data_by_product = main_models.LabelingData.objects.filter(
                    category__product__name=select_product
                )

                # 선택한 제품에 해당하는 카테고리를 가져옴
                categories_by_product = main_models.Category.objects.filter(product__name=select_product)

                # emotion 데이터
                emotions = main_models.Emotion.objects.all()

                with BytesIO() as b:
                    writer = pd.ExcelWriter(b, engine="xlsxwriter")

                    for category in categories_by_product: # [제품군에 해당하는 카테고리]
                        keywords = {}
                        counts = {}
                        export_dict = {}
                        for emotion in emotions: # [긍정, 부정, 중립 객체]
                            kewords_in_labeled_data = labeled_data_by_product.filter(
                                category=category, emotion=emotion
                                ).values_list(
                                "target", "phenomenon"
                                ).distinct().order_by("target", "phenomenon")                            

                            #### 같은 대상(target)을 딕셔너리 키로 묶기 ####
                            keyword_dict = dict()
                            for keword_in_labeled_data in kewords_in_labeled_data:
                                target = keword_in_labeled_data[0] or ""
                                phenomenon = keword_in_labeled_data[1] or ""
                                if target not in keyword_dict:
                                    keyword_dict[target] = list()
                                if not any(phenomenon.startswith(keyword) for keyword in keyword_dict.get(target, [])):
                                    keyword_dict[target].append(phenomenon)
                                    
                            export_keyword_by_category=list()
                            for key, val_list in keyword_dict.items():
                                for val in val_list:
                                    export_keyword_by_category.append(key + " AND " + val)

                            # count = 감정별 키워드쌍의 개수를 세고 제일 많은 것을 골라 행을 채우는 용도
                            counts[emotion.e_name + "_keyword"] = len(export_keyword_by_category)

                            # 감정별 데이터 쌍을 저장
                            keywords[emotion.e_name + "_keyword"] = export_keyword_by_category

                        max_count = max(counts.values())
                        export_dict = {
                            "Product_Group": [select_product] * max_count,
                            "Type": ["3F_Ergonomics"] * max_count,
                            "Category": [category.name] * max_count,
                            "긍정 키워드": keywords["positive_keyword"],
                            "부정 키워드": keywords["negative_keyword"],
                            "중립 키워드": keywords["neutral_keyword"],
                        }
                        df = pd.DataFrame.from_dict(export_dict, orient="index")
                        df = df.transpose()
                        df.to_excel(writer, sheet_name=category.name, index=False)
                        format_change(writer, category)
                    writer.save()
                    encoded_filename = urllib.parse.quote(select_product)
                    content_type = "application/vnd.ms-excel"
                    response = HttpResponse(b.getvalue(), content_type=content_type)
                    response["Content-Disposition"] = (
                        'attachment; filename="' + encoded_filename + '.xlsx"'
                    )
                    return response

            # elif request.POST["export"] == ".csv export":
            #     ####---- HttpResponse 설정 ----####
            #     product = request.POST["product"]
            #     response = HttpResponse(content_type="text/csv")
            #     response["Content-Disposition"] = (
            #         "attachment; filename="
            #         + product
            #         + "_"
            #         + datetime.now().strftime("%Y-%m-%d_%I-%M-%S_%p")
            #         + ".csv"
            #     )
            #     response.write("\ufeff".encode("utf8"))

            #     ####---- csv 파일 만들기 ----####
            #     writer = csv.writer(response)
            #     reviews = list(
            #         main_models.Review.objects.filter(
            #             first_status=True, category_product=product
            #         ).values_list("review_id", flat=True)
            #     )
            #     review_contents = list(
            #         main_models.Review.objects.filter(
            #             first_status=True, category_product=product
            #         ).values_list("review_content", flat=True)
            #     )
            #     result = [[""]] * len(reviews)
            #     for i in range(len(reviews)):
            #         categorys = main_models.LabelingData.objects.filter(
            #             review_id=reviews[i], category_id__category_product=product
            #         ).values_list("category_id__category_middle", flat=True)
            #         review_category = ""
            #         for category in categorys:
            #             review_category += category + "and"
            #         review_category = review_category[:-3]
            #         result[i] = [reviews[i], review_contents[i], review_category]
            #     print(result[0])

            #     # 6. csv 파일 만들기
            #     writer.writerow(["리뷰 번호", "리뷰 원문", "카테고리"])
            #     for rlt in result:
            #         writer.writerow(rlt)
            #     return response

            # else:
            #     print("error")
        else:
            print("error")

    except Exception as identifier:
        print(identifier)
    return render(request, "output/output.html")