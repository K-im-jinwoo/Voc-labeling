# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    image = models.ImageField(upload_to="profile/", null=True)
    name = models.CharField(max_length=256, null=True)
    manager = models.BooleanField(default=False) # 관리자 권한 여부


class UserProfile(models.Model):
    profile_picture = models.ImageField(upload_to="profile_pictures/")


# 제품 모델 
# ex) id:1, k_name:청소기, e_name:cleaner
class Product(models.Model):
    id = models.AutoField(primary_key=True)
    k_name = models.CharField(max_length=256)
    e_name = models.CharField(max_length=256)

    def __str__(self):
        return f"{self.id} - {self.k_name} - {self.e_name}"


# 카테고리 모델 
# ex) product: Product, id: 1, k_name: 흡입력, e_name:suction_power, color: #ffffff
class Category(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="category_products")
    id = models.AutoField(primary_key=True)
    k_name = models.CharField(max_length=256)
    e_name = models.CharField(max_length=256)
    color = models.CharField(max_length=256)

    def __str__(self):
        return f"{self.product} - {self.id} - {self.k_name} - {self.e_name} - {self.color}"


# 리뷰 데이터 모델
# product: Product, assigned_user: 할당된 유저, worked_user: 작업한 유저, id: 1, number: 리뷰 번호, content: 리뷰
# is_labeled: 라벨링 여부, is_trashed: 데이터 버림 여부, model_name: 모델 이름, model_code: 모델 코드, date_writted: 리뷰 작성 날짜, date_uploaded: 데이터 업로드 날짜
class Review(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="review_products")
    assigned_user = models.ForeignKey("Profile", on_delete=models.CASCADE, null=True, blank=True, related_name="review_assigned_users")
    worked_user = models.ForeignKey("Profile", on_delete=models.CASCADE, null=True, blank=True, related_name="review_worked_users")
    id = models.AutoField(primary_key=True)
    number = models.IntegerField()
    content = models.TextField()
    is_labeled = models.BooleanField(default=False) # true: 라벨링됨
    is_trashed = models.BooleanField(default=False) # true: 버림
    model_name = models.CharField(null=True, blank=True, max_length=256)
    model_code = models.CharField(null=True, blank=True, max_length=256)
    date_writted = models.DateField(null=True, blank=True)
    date_uploaded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Product_k_name:{self.product.k_name} - Review_id:{self.id}"


# 라벨링 데이터 모델
# review: Review, category: Category, id: 1, emotion: 긍정/부정/중립, target: 대상, phenomenon: 현상, date_labeled: 라벨링된 날짜
class LabelingData(models.Model):
    review = models.ForeignKey("Review", on_delete=models.CASCADE, related_name="labeling_data_reviews")
    category = models.ForeignKey("Category", on_delete=models.CASCADE, related_name="labeling_data_categories")
    emotion = models.ForeignKey("Emotion", on_delete=models.PROTECT, related_name="labeling_data_emotion")
    id = models.AutoField(primary_key=True)
    target = models.CharField(max_length=256, null=True, blank=True)
    phenomenon = models.CharField(max_length=256, null=True, blank=True)
    date_labeled = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.review.id} - ({self.review.product.k_name} - {self.category.k_name}) - {self.id}"
    
class Emotion(models.Model):
    id = models.IntegerField(primary_key=True)
    k_name = models.CharField(max_length=256)
    e_name = models.CharField(max_length=256)

    def __str__(self):
        return f"{self.id} - {self.k_name} - {self.e_name}"
    