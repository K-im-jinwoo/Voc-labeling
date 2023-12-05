from django.shortcuts import render

from mainapp.models import FirstLabeledData


def dummydummy(request):
    message = ""
    product = ""
    category = ""

    if request.method == "POST":
        if request.POST.get("category_product") != "" and request.POST.get("category_middle") != "":
            dummy_data = FirstLabeledData.objects.filter(
                category_id__category_product=request.POST.get("category_product"),
                category_id__category_middle=request.POST.get("category_middle"),
                first_labeled_target=request.POST.get("first_labeled_target"),
                first_labeled_expression=request.POST.get("first_labeled_expression"),
                first_labeled_emotion=request.POST.get("first_labeled_emotion"), )
            message = request.POST.get("category_product") + "제품의 " + request.POST.get(
                "category_middle") + "카테고리의 " + request.POST.get("first_labeled_emotion") + request.POST.get(
                "first_labeled_target") + " - " + request.POST.get(
                "first_labeled_expression") + "을 " + str(dummy_data.count()) + "개 지웠습니다. "
            dummy_data.delete()
            product = request.POST.get("category_product")
            category = request.POST.get("category_middle")

    context = {"message": message, "product": product, "category": category}
    return render(request, 'labelingapp/dummy_to_trashcan.html', context=context)
