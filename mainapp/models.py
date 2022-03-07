from django.contrib.auth.models import User
from django.db import models


# Create your models here.


class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_middle = models.CharField(max_length=256)
    category_color = models.CharField(max_length=256)
    category_product = models.CharField(max_length=256)

    def __str__(self):
        return str(self.category_id) + ' - ' + str(self.category_middle)


class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    review_number = models.CharField(max_length=256)
    category_product = models.CharField(max_length=256)
    review_content = models.TextField()
    first_status = models.BooleanField()
    second_status = models.BooleanField()
    dummy_status = models.BooleanField()
    first_labeled_id=models.CharField(max_length=256)
    second_labeled_id=models.CharField(max_length=256)

    def __str__(self):
        return str(self.review_id) + ' - ' + str(self.category_product)


class First_Labeled_Data(models.Model):
    first_labeled_id = models.AutoField(primary_key=True)
    first_labeled_emotion = models.CharField(max_length=256)
    first_labeled_target = models.CharField(max_length=256)
    first_labeled_expression = models.CharField(max_length=256)
    category_id = models.ForeignKey("Category", on_delete=models.CASCADE)
    review_id = models.ForeignKey("Review", on_delete=models.CASCADE)

    def __str__(self):
        return str(self.first_labeled_id) + ' - ' + str(self.first_labeled_emotion)


class Second_Labeled_Data(models.Model):
    second_labeled_id = models.AutoField(primary_key=True)
    second_labeled_emotion = models.CharField(max_length=256)
    second_labeled_target = models.CharField(max_length=256)
    second_labeled_expression = models.CharField(max_length=256)
    category_id = models.ForeignKey("Category", on_delete=models.CASCADE)
    review_id = models.ForeignKey("Review", on_delete=models.CASCADE)

    def __str__(self):
        return str(self.second_labeled_id) + ' - ' + str(self.second_labeled_emotion)


class Result(models.Model):
    result_id = models.AutoField(primary_key=True)
    second_labeled_id = models.ForeignKey("Second_Labeled_Data", on_delete=models.CASCADE)

    result_emotion = models.CharField(max_length=256)
    result_target = models.CharField(max_length=256)
    result_expression = models.CharField(max_length=256)