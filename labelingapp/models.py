from django.db import models


# Create your models here.

class First_Labled_Data(models.Model):
    first_labeled_id = models.CharField(primary_key=True, max_length=256)
    first_labeled_emotion = models.CharField(max_length=256)
    first_labeled_target = models.CharField(max_length=256)
    first_labeled_expression = models.CharField(max_length=256)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    review_id = models.ForeignKey(Review, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.first_labeled_id) + ' - ' + str(self.first_labeled_emotion)


class Second_Labled_Data(models.Model):
    second_labeled_id = models.CharField(primary_key=True, max_length=256)
    second_labeled_emotion = models.CharField(max_length=256)
    second_labeled_target = models.CharField(max_length=256)
    second_labeled_expression = models.CharField(max_length=256)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    review_id = models.ForeignKey(Review, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.second_labeld_id) + ' - ' + str(self.second_labeld_emotion)


