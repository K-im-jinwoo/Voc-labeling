# from main.models import Category
# from django.shortcuts import render

# def secondContent(request):
#     categories = Category.objects.all()
#     product_names = [category.category_product for category in categories if category.category_product]
#     return render(request, 'content/secondContent.html', {'product_names': product_names})