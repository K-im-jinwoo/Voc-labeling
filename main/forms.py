from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm

from django import forms
from .models import UserProfile
from mainapp.models import Profile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["profile_picture"]


class AccountUpdateForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].disabled = True


class ProfileCreationForm(ModelForm):
    class Meta:
        model = Profile
        fields = ["image", "name"]
