# -*- coding: utf-8 -*-
from django.core.files.storage import FileSystemStorage
from django.db.models import Max
from django.http import HttpResponseRedirect
from django.shortcuts import render
import pandas as pd
import io
import sys
from django.urls import reverse
from LG_Project.settings.base import BASE_DIR
from main import models as main_models
import time

# 카테고리 삭제
def delete_category(request):
    if request.method == "POST":
        category_middle = request.POST.get("category_middle")
        category = main_models.Category.objects.filter(category_middle=category_middle)[
            0
        ]
        category.delete()
        url = (
            reverse("upload:upload") + f"?category_product={category.category_product}"
        )
    return HttpResponseRedirect(url)

# 코드 실행 이전 시간 기록
# start_time = time.time()

def cleansing(csv_file, is_csv=True):
    
    # .csv 파일 불러오기
    if is_csv:
        raw_data = pd.read_csv("." + csv_file, encoding="utf-8")
    else:
        raw_data = csv_file
    
    # 필요한 열 선택 및 중복 제거
    data = raw_data[["Date", "Model Name", "Model Code", "Original Comments"]]
    data = data.drop_duplicates(["Original Comments"])
    upload_data = data.copy()

    # Original Comment 텍스트 클리닝 - 불필요한 문자열 제거
    upload_data["Original Comments"] = (
        upload_data["Original Comments"]
        .str.replace(pat=r"<[^>]*>", repl=r"", regex=True)  # HTML 태그 제거
        .str.replace(pat=r"(<[a-zA-Z0-9\_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-\.]+>)", repl=r"", regex=True)  # 이메일 주소 제거
        .str.replace("_", "") # _제거
        .str.replace(pat=r"[\r|\n]", repl=r"", regex=True) # \r, \n 제거
        .str.replace(
            pat=r"""(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))""",
            repl=r"",
            regex=True,
        ) # url 제거
        .str.replace(
            pat=r"([ㄱ-ㅎㅏ-ㅣ]+)", repl=r"", regex=True
        ) # 자음, 모음 제거
        .str.replace(
            pat=r"[^\w\s]", repl=r"", regex=True
        ) # 알파벳, 숫자, 공백 제외 모든 문자 제거
        .str.replace("1n", "") # "1n" 문자열 제거
        .str.replace("_", "") # "_" 문자열 제거
        .str.replace(
            pat=r"^[a-zA-Z\s]+$", repl=r"", regex=True
        ) # 모두 영어인 행 공백으로 대체
        .str.replace(
            pat=r"^[0-9\s]+$", repl=r"", regex=True
        ) # 모두 숫자인 행 공백으로 대체
        .str.strip() # 좌우 공백 제거
    )

    # 아이디 관련 단어 제거
    upload_data["Original Comments"] = (
        upload_data["Original Comments"]
        .str.replace(
            pat=r"(ID|아이디|id)\s[a-zA-Z0-9]+", repl=r"", regex=True
        )
    )

    # 주문번호 관련 단어 제거
    upload_data["Original Comments"] = (
        upload_data["Original Comments"]
        .str.replace(
            pat=r"(주문번호|결제번호|구매번호|주문\s번호|결제\s번호|구매\s번호)\s[a-zA-Z0-9]+", repl=r"", regex=True
        )
    )

    # " " -> "" 처리 후 중복 리뷰 제거
    upload_data["temp"] = upload_data["Original Comments"].str.replace(" ", "")
    upload_data = upload_data.drop_duplicates(["temp"]).drop(["temp"], axis=1)

    # 코드 실행 후 시간 기록
    # end_time = time.time()
    # execution_time = end_time - start_time
    # print("코드 실행 시간: ", execution_time)
    return upload_data

def upload_main(request):
    try:
        # 제품 선택
        if request.method == "GET":
            context = dict()
            context["product_names"] = (
                main_models.Product.objects.all().values("name").distinct()
            )
            request.session["category_product"] = "제품명 선택"
            if request.GET.get("category_product"):
                request.session["category_product"] = request.GET.get(
                    "category_product"
                )
            context["category_detail"] = main_models.Category.objects.filter(
                name=request.session["category_product"]
            )
            category_product = request.POST.get("category_product")
            return render(request, "upload/upload_main.html", context)

        # 제품 추가
        elif request.method == "POST":
            if request.POST.get("category_add"):
                product = main_models.Product()
                category = main_models.Category()
                product.name = request.POST.get("category_add")
                product.save()
                category.product = main_models.Product.objects.get(name=request.POST.get("category_add"))
                category.name = "기타"
                category.color = "#c8c8c850"
                category.save()
                return HttpResponseRedirect(reverse("upload:upload"))

            # 제품명 변경
            if request.POST.get("category_update"):
                category_product = request.POST.get("category_product")
                category_update = request.POST.get("category_update")

                # 해당하는 제품명 변경
                duplicate_product = main_models.Product.objects.get(
                    name=category_product
                )
                duplicate_product.name  = category_update
                duplicate_product.save()

                return HttpResponseRedirect(reverse("upload:upload"))
            
            ### 여기서부터
            # 카테고리 추가
            if request.POST.get("form-type") == "formOne":
                category = main_models.Category()
                category.category_product = request.session["category_product"]
                category.category_middle = request.POST.get("category_middle", "")
                temp_color = str(request.POST.get("category_color", "")) + "50"
                category.category_color = temp_color
                category.save()
                category_product = request.GET.get("category_product")
                url = (
                    reverse("upload:upload")
                    + f"?category_product={category.category_product}"
                )
                return HttpResponseRedirect(url)

            if request.POST.get("session_product"):
                print("제품삭제 뷰")
                session_product = request.POST.get("session_product")
                print(session_product)
                product_review = main_models.Review.objects.filter(
                    category_product=session_product
                ).delete()
                product_category = main_models.Category.objects.filter(
                    category_product=session_product
                ).delete()
                print(product_category)
                return HttpResponseRedirect(reverse("upload:upload"))

            elif request.POST.get("form-type") == "formTwo":
                # upload_files 변수에 파일 저장시 Review 모델에 저장
                if request.FILES["upload_file"]:
                    # csv 형식으로 저장
                    upload_file = request.FILES["upload_file"]
                    if not upload_file.name.endswith("csv"):
                        request.session["message"] = "<<Error>> 엑셀 형식으로 업로드 해주세요"
                        request.session.set_expiry(3)
                        return HttpResponseRedirect(reverse("upload:upload"))

                    # 데이터 전처리 및 정제 작업
                    fs = FileSystemStorage()
                    filename = fs.save(upload_file.name, upload_file)
                    upload_file_url = fs.url(filename)
                    dbframe = cleansing(upload_file_url, is_csv=True)
                    fs.delete(str(BASE_DIR) + upload_file_url)

                    # 중복 제거하기
                    dbreviews = main_models.Review.objects.filter(
                        category_product=request.POST.get("category_product")
                    ).values_list("review_content", flat=True)
                    dbreviews = pd.DataFrame({"Original Comments": dbreviews})

                    dbframe = (
                        pd.merge(dbreviews, dbframe, how="outer", indicator=True)
                        .query('_merge == "right_only"')
                        .drop(columns=["_merge"])
                    )

                    # 현재 model의 category_product별로 최대값을 기준으로 review_number을 갱신하기 위한 변수 category_max_num
                    category_max_num = (
                        main_models.Review.objects.filter(
                            category_product=request.POST.get("category_product")
                        )
                        .aggregate(temp=Max("review_number"))
                        .get("temp", None)
                    )
                    if category_max_num == None:
                        category_max_num = 0
                    dbframe.reset_index(inplace=True)
                    dbframe["index"] = dbframe["index"] + int(category_max_num) + 1
                    # dbframe = pd.merge(dbframe, model_name, left_index=True, right_index=True, how='left')
                    # print(dbframe)
                    # print("model",model_name)
                    # 저장 부분
                    print(dbframe)
                    review_obj = [
                        main_models.Review(
                            review_content=row["Original Comments"],
                            category_product=request.POST.get("category_product"),
                            review_number=row["index"],
                            model_name=row["Model Name"],
                            model_code=row["Model Code"],
                        )
                        for _, row in dbframe.iterrows()
                    ]
                    main_models.Review.objects.bulk_create(review_obj)
                    request.session["message"] = "업로드가 완료되었습니다."
                    # request.session.set_expiry(3)
                    url = (
                        reverse("upload:upload")
                        + f'?category_product={request.POST.get("category_product")}'
                    )
                    return HttpResponseRedirect(url)

            elif request.POST.get("form-type") == "formThree":
                try:
                    textarea_value = request.POST.get("textarea", None)
                    if textarea_value is not None and textarea_value != "":
                        input_text = textarea_value
                        dbframe = pd.read_csv(io.StringIO(input_text), sep="\t")
                        print(dbframe)
                        print("Before cleansing")
                        inputdata = cleansing(dbframe, is_csv=False)
                        print("After cleansing")
                        dbreviews = main_models.Review.objects.filter(
                            category_product=request.POST.get("category_product")
                        ).values_list("review_content", flat=True)
                        dbreviews = pd.DataFrame({"Original Comments": dbreviews})
                        inputdata = (
                            pd.merge(dbreviews, inputdata, how="outer", indicator=True)
                            .query('_merge == "right_only"')
                            .drop(columns=["_merge"])
                        )

                        category_max_num = (
                            main_models.Review.objects.filter(
                                category_product=request.POST.get("category_product")
                            )
                            .aggregate(temp=Max("review_number"))
                            .get("temp", None)
                        )
                        if category_max_num == None:
                            category_max_num = 0
                        inputdata.reset_index(inplace=True)
                        inputdata["index"] = (
                            inputdata["index"] + int(category_max_num) + 1
                        )
                        print(inputdata.columns)
                        review_obj = [
                            main_models.Review(
                                review_content=row["Original Comments"],
                                category_product=request.POST.get("category_product"),
                                review_number=row["index"],
                                model_name=row["Model Name"],
                                model_code=row["Model Code"],
                            )
                            for _, row in inputdata.iterrows()
                        ]
                        main_models.Review.objects.bulk_create(review_obj)
                        request.session["message"] = "업로드가 완료되었습니다."
                        url = (
                            reverse("upload:upload")
                            + f'?category_product={request.POST.get("category_product")}'
                        )
                        return HttpResponseRedirect(url)
                    else:
                        request.session[
                            "message"
                        ] = "<<Error>> 업로드 하려는 파일의 내용을 붙여넣은 후 업로드 해주세요."
                        request.session.set_expiry(3)
                        return HttpResponseRedirect(reverse("upload:upload"))
                except Exception as e:
                    print(
                        f"Error at line {sys.exc_info()[-1].tb_lineno}: {e}"
                    )  # 추가한 라인; 발생하는 오류와 몇 번째 줄에서 발생하는지 출력합니다.
                    raise e
        return render(request, "upload/upload_main.html", {})

    # 예외 처리
    except Exception as identifier:
        print(identifier)

    return render(request, "upload/upload_main.html", {})
