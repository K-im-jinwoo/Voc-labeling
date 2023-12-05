# -*- coding: utf-8 -*-
from django.db import models


class DashCategory(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_middle = models.CharField(max_length=256)
    category_color = models.CharField(max_length=256)
    category_product = models.CharField(max_length=256)

    def __str__(self):
        return str(self.category_id) + " - " + str(self.category_middle)


class DashReview(models.Model):
    review_id = models.AutoField(primary_key=True)
    category_product = models.CharField(max_length=256, null=False)
    review_number = models.IntegerField(null=False)
    review_content = models.TextField(null=False)
    first_status = models.BooleanField(default=False)
    second_status = models.BooleanField(default=False)
    dummy_status = models.BooleanField(default=False)
    first_assign_user = models.TextField(default="0", null=True)
    second_assign_user = models.TextField(default="0", null=True)
    model_name = models.TextField(default="", null=True)
    model_code = models.TextField(default="", null=True)

    def __str__(self):
        return str(self.review_id) + " - " + str(self.category_product)


class DashFirstLabeledData(models.Model):
    first_labeled_id = models.AutoField(primary_key=True)
    first_labeled_emotion = models.CharField(max_length=256)
    first_labeled_target = models.CharField(max_length=256)
    first_labeled_expression = models.CharField(max_length=256)
    category_id = models.ForeignKey("DashCategory", on_delete=models.CASCADE)
    review_id = models.ForeignKey("DashReview", on_delete=models.CASCADE)
    model_name = models.TextField(default="", null=True)
    model_code = models.TextField(default="", null=True)

    def __str__(self):
        return str(self.first_labeled_id) + " - " + str(self.first_labeled_emotion)


class DashSecondLabeledData(models.Model):
    second_labeled_id = models.AutoField(primary_key=True)
    second_labeled_emotion = models.CharField(max_length=256)
    second_labeled_target = models.CharField(max_length=256)
    second_labeled_expression = models.CharField(max_length=256)
    category_id = models.ForeignKey("DashCategory", on_delete=models.CASCADE)
    review_id = models.ForeignKey("DashReview", on_delete=models.CASCADE)

    def __str__(self):
        return str(self.second_labeled_id) + " - " + str(self.second_labeled_emotion)


class DashResult(models.Model):
    result_id = models.AutoField(primary_key=True)
    second_labeled_id = models.ForeignKey(
        "DashSecondLabeledData", on_delete=models.CASCADE
    )
    result_emotion = models.CharField(max_length=256)
    result_target = models.CharField(max_length=256)
    result_expression = models.CharField(max_length=256)


class DashWebStatus(models.Model):
    status_id = models.AutoField(primary_key=True)
    status_name = models.TextField(default="")
    status_value = models.TextField(default="")
