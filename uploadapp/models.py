from django.db import models

# Create your models here.

class Review(models.Model):
    review_id = models.CharField(primary_key=True, max_length=256)
    review_number = models.CharField(max_length=256)
    category_product = models.CharField(max_length=256)
    review_content = models.TextField()
    first_status = models.BooleanField()
    second_status = models.BooleanField()
    dummy_status = models.BooleanField()
    first_labeled_id = models.ForeignKey(First_Labled_Data, on_delete=models.CASCADE)
    second_labeled_id = models.ForeignKey(Second_Labled_Data, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.review_id) + ' - ' + str(self.category_product)


class Category(models.Model):
    category_id = models.CharField(primary_key=True, max_length=256)
    category_middle = models.CharField(max_length=256)
    category_color = models.CharField(max_length=256)
    category_product = models.CharField(max_length=256)

    def __str__(self):
        return str(self.category_id) + ' - ' + str(self.category_middle)


