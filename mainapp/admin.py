from django.contrib import admin

# Register your models here.

from .models import Category, Review, FirstLabeledData, Result, SecondLabeledData

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_product', 'category_middle', 'category_color']

    def delete_model(self, request, obj):
        obj.category_product = None
        obj.save()

    actions = ['delete_selected']

admin.site.register(Category, CategoryAdmin)
admin.site.register(Review)
admin.site.register(FirstLabeledData)
admin.site.register(SecondLabeledData)
admin.site.register(Result)