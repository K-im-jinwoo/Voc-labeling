from django.contrib import admin

# Register your models here.

from .models import Category, Review, FirstLabeledData

admin.site.register(Category)
admin.site.register(Review)
admin.site.register(FirstLabeledData)