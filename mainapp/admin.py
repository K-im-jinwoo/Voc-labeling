from django.contrib import admin

# Register your models here.

from .models import Category, Review

admin.site.register(Category)
admin.site.register(Review)