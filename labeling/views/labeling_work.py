from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from main import models as main_models

# 할당된 제일 최근 리뷰 데이터와 자동 라벨링 해주는 함수
@csrf_exempt
def find_review_auto_labeling(product_name, user_profile):

    # 첫번째 데이터
    first_data = main_models.Review.objects.filter(
        product__name=product_name, assigned_user=user_profile, is_labeled=False, is_trashed=False
        ).order_by("pk").first()
    
    # 기존 데이터
    exist_datas = main_models.LabelingData.objects.filter(category__product__name=product_name)
    
    # 자동 라벨링 데이터 리스트
    unique_entries = set()  # Create a set to store unique entries
    auto_labeling_datas = []

    for exist_data in exist_datas:
        if (
            first_data.content.__contains__(exist_data.target)
            and first_data.content.__contains__(exist_data.phenomenon)
        ):
            entry = (
                exist_data.category.name,
                exist_data.category.color,
                exist_data.target,
                exist_data.phenomenon,
                exist_data.emotion.k_name,
            )

            # Check if the entry is not already in the set before adding it
            if entry not in unique_entries:
                auto_labeling_datas.append({
                    "category": exist_data.category.name,
                    "category_color": exist_data.category.color,
                    "target": exist_data.target,
                    "phenomenon": exist_data.phenomenon,
                    "emotion": exist_data.emotion.e_name,
                })
                unique_entries.add(entry)

    review_auto_labeling = {
        "id": first_data.pk,
        "content": first_data.content,
        "auto_labeling": auto_labeling_datas
    }

    # 프론트에게 넘겨 줄 데이터 형식 => review_auto_labeling
	# review_auto_labeling = {
	# 	"id": int,
	# 	"content": "--------",
	# 	"auto_labeling": [
	# 		{"category": "", "category_color": "", "target": "" , "phenomenon": "", "emotion": ""}, // emotion은 영어로 표현("positive","negative","netural")
	# 		{"category": "", "category_color": "", "target": "" , "phenomenon": "", "emotion": ""},
	# 		...
	# 	]
    # }
    return review_auto_labeling

# 사용자와 제품군에 따라 데이터 할당 정보
def get_assigned_info(product_name, user_profile):
    # 모든 Product
    product = main_models.Product.objects.get(name=product_name)

    # assign정보를 알기위해 모든 review를 가져옴
    current_user_review = main_models.Review.objects.select_related("product", "assigned_user__user").filter(product=product, assigned_user=user_profile)

    # product_names
    assigned_info = {
        # review 데이터중 해당 제품과 assigned_user가 현재 유저인 경우가 존재하는지에 대한 필드
        "is_assigned": current_user_review.exists(), 
        "assigned_num": current_user_review.count()
    }

    return assigned_info

# 할당 작업
def assignment_review(product_name, count, user_profile):
    try:
        reviews_to_update = main_models.Review.objects.filter(
            product__name=product_name, is_labeled=False, is_trashed=False, assigned_user__isnull=True
        ).order_by("id")[:count]

        for review in reviews_to_update:
            review.assigned_user = user_profile
            review.save()
        return True
    except:
        return False
    

# 라벨링 페이지의 모든 동작
@csrf_exempt
def labeling_work(request):
    try:
        user_profile = main_models.Profile.objects.get(user=request.user)
        context=dict()
        if request.method == "GET":
            if "product_name" in request.GET: # 할당 -> 리뷰데이터 + 자동라벨링 보여주는 파트
                context = dict()
                product_name = request.GET["product_name"]
                get_is_assigned = request.GET["is_assigned"]
                is_assigned = False if get_is_assigned.lower() == "false" else True
                count = int(request.GET["count"])
                print("product_name: ", product_name, "\nproduct_name_type: ", type(product_name))
                print("is_assigned: ", is_assigned, "\nis_assigned_type: ", type(is_assigned))
                print("count: ", count, "\ncount_type: ", type(count))

                print("11111")
                # is_assigned=True인 경우(count에 따라 할당리뷰를 보여줄지, 추가할당 후 할당 리뷰를 보여줄지 결정)
                if is_assigned:
                    print("222222222")
                    if count == 0: # 이미 할당된 데이터가 존재해서 바로 리뷰 보여주면됨
                        pass
                    elif count != 0: # 할당된 데이터가 존재하지만 추가할당을 원하는 경우
                        current_user_count = main_models.Review.objects.filter(assigned_user=user_profile).count()
                        total_count = current_user_count + count
                        if total_count <= 1000: # 할당 작업
                            result = assignment_review(product_name, count, user_profile)
                            if not result:
                                raise ValueError("할당 실패")
                        else:
                            raise ValueError("할당 데이터 개수가 1000개를 초과함") # 프론트에 에러 처리보내기

                # is_assigned=False 경우(할당된 데이터가 없으므로 할당 작업을 거치고 review데이터 보내기)
                elif not is_assigned:
                    print("33333333333")
                    if count <= 1000:
                        result = assignment_review(product_name, count, user_profile)
                        if not result:
                            raise ValueError("할당 실패")
                    else:
                        raise ValueError("할당 데이터 개수가 1000개를 초과함")
                    
                assigned_info = get_assigned_info(product_name, user_profile)
                review_info = find_review_auto_labeling(product_name, user_profile)

                context["assigned_info"] = assigned_info
                context["review_info"] = review_info

            ## labeling page 탭을 누르고 처음 들어왔을 경우 기본적으로 프론트한테 전달해야하는 데이터 -> 프론트가 보관해두고 계속 써야할 데이터
            elif "product_name" not in request.GET:
                # 모든 Product
                qs_product = main_models.Product.objects.all()

                # 모든 Category
                qs_category = main_models.Category.objects.select_related("product").all()

                # assign정보를 알기위해 모든 review를 가져옴
                qs_review = main_models.Review.objects.select_related("product", "assigned_user__user").all()

                # product_names
                product_names = []
                for product in qs_product:
                    product_names.append({
                        "product_name": product.name,
                        # review 데이터중 해당 제품과 assigned_user가 현재 유저인 경우가 존재하는지에 대한 필드
                        "is_assigned": qs_review.filter(product=product, assigned_user=user_profile).exists(), 
                        "assigned_num": qs_review.filter(product=product, assigned_user=user_profile).count()
                    })

                # category_list
                category_list = {}
                for product in qs_product:
                    categories_by_product = qs_category.filter(product=product)
                    name_color_list=[]
                    for category in categories_by_product:
                        name_color_list.append({"category":category.name, "color":category.color})
                    category_list[product.name] = name_color_list

                # emotion
                emotion = main_models.Emotion.objects.all().values_list("e_name", flat=True)
                context["product_names"] = product_names
                context["category_list"] = category_list
                context["emotion"] = list(emotion)
            return render(request, "labeling/labeling_work.html", context=context)
        
        elif request.method == "POST":
            print("555555555")
            if request.POST.get("form-type") == "labeling_form": # 라벨링 작업
                # 프론트에서 받아야할 데이터
                # {
                #     "review_info" : {
                #         "product_name": "",
                #         "review_id": [int]
                #     },
                #     "labeling_data_list": [
                #         {
                #             "category": "",
                #             "target": "",
                #             "phenomenon": "",
                #             "emotion": ""
                #         },
                #         {
                #             "category": "",
                #             "target": "",
                #             "phenomenon": "",
                #             "emotion": ""
                #         }, ...
                #     ]
                # }
                review_info = request.POST["review_info"]
                labeling_data_list = request.POST["labeling_data_list"]
                
                product_name = review_info["product_name"]
                qs_categories = main_models.Category.objects.filter(product__name=product_name)
                qs_emotions = main_models.Emotion.objects.all()

                # 작업 데이터 저장
                create_labeling_data_list=[]
                for labeling_data in labeling_data_list:
                    create_labeling_data_list.append(main_models.LabelingData(
                        review_id=review_info["review_id"],
                        category=qs_categories.get(name=labeling_data["category"]),
                        target=labeling_data["target"],
                        phenomenon=labeling_data["phenomenon"],
                        emotion=qs_emotions.get(e_name=labeling_data["emotion"])
                    ))
                main_models.LabelingData.objects.bulk_create(create_labeling_data_list)
                
                # 리뷰의 라벨링 상태 업데이트
                main_models.Review.objects.filter(id=review_info["review_id"]).update(assigned_user=None, worked_user=user_profile, is_labeled=True)
            
            elif request.POST.get("form-type") == "dummy_form": # 리뷰 -> is_trashed=True작업
                # 프론트에서 받아야 할 데이터
                # {
                #     "product_name": "",
                #     "review_id": [int]
                # }
                product_name = request.POST["product_name"]
                review_id = request.POST["review_id"]

                main_models.Review.objects.filter(id=review_id).update(assigned_user=None, worked_user=user_profile, is_trashed=True)      

            # 다음 리뷰와 자동 라벨링 데이터 가져오기
            assigned_info = get_assigned_info(product_name, user_profile)
            review_info = {}
            if assigned_info["is_assigned"]: # 작업 후 할당된 데이터가 없는 경우
                review_info = find_review_auto_labeling(product_name, user_profile)

            context["assigned_info"] = assigned_info
            context["review_info"] = review_info
            return render(request, "labeling/labeling_work.html", context=context)

    # 예외처리
    except Exception as identifier:
        print(identifier)
    context = dict()
    return render(request, "labeling/labeling_work.html", context=context)