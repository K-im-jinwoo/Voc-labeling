from django.contrib import admin

from . import models as main_models


class CategoryAdmin(admin.ModelAdmin):
    list_display = ["category_product", "category_middle", "category_color"]

    def delete_model(self, request, obj):
        obj.category_product = None
        obj.save()

    actions = ["delete_selected"]


class ReviewAdmin(admin.ModelAdmin):
    list_display = ['category_product']
    list_filter = ['category_product']

    def delete_selected_reviews(modeladmin, request, queryset):
        # Define the chunk size
        chunk_size = 1000
        selected_reviews = list(queryset)  # Convert the QuerySet to a list
        total_reviews = len(selected_reviews)

        for i in range(0, total_reviews, chunk_size):
            chunk = selected_reviews[i:i + chunk_size]
            # Delete reviews in chunks of 1000 or less
            main_models.Review.objects.filter(pk__in=[review.pk for review in chunk]).delete()

        modeladmin.message_user(
            request,
            f"Selected {total_reviews} reviews have been deleted in chunks of 1000 or less."
        )

    delete_selected_reviews.short_description = "Delete selected reviews in chunks of 1000 or less"



admin.site.register(main_models.Category, CategoryAdmin)
admin.site.register(main_models.Review,  ReviewAdmin)
admin.site.register(main_models.FirstLabeledData)
admin.site.register(main_models.SecondLabeledData)
admin.site.register(main_models.Result)
