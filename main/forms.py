from django.contrib.auth.forms import UserCreationForm
from django import forms

from . import models


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = models.UserProfile
        fields = ["profile_picture"]


class AccountUpdateForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].disabled = True


class ProfileCreationForm(forms.ModelForm):
    class Meta:
        model = models.Profile
        fields = ["image", "name"]
