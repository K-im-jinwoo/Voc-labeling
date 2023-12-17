from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView

from main import (
    decorators as main_decorators, 
    forms as main_forms, 
    models as main_models
)


class AccountCreateView(CreateView):
    model = User
    form_class = UserCreationForm  # 기본적인 userform을 제공해준다.
    success_url = reverse_lazy(
        "main:login"
    )  # reverse는 함수형, reverse_lazy는 class에서 사욯한다.
    template_name = "main/signup.html"


class AccountLoginView(LoginView):
    form_class = AuthenticationForm
    template_name = "main/login.html"


class AccountDetailView(DetailView):
    model = User
    context_object_name = "target_user"
    template_name = "main/account.html"

    def get(self, *args, **kwargs):
        if (
            self.request.user.is_authenticated
            and self.get_object() == self.request.user
        ):
            return super().get(*args, **kwargs)
        else:
            return HttpResponseForbidden()

    def post(self, *args, **kwargs):
        if (
            self.request.user.is_authenticated
            and self.get_object() == self.request.user
        ):
            return super().get(*args, **kwargs)
        else:
            return HttpResponseForbidden()


class AccountUpdateView(UpdateView):
    model = User
    context_object_name = "target_user"
    form_class = main_forms.AccountUpdateForm
    success_url = reverse_lazy("main:main")
    template_name = "main/update.html"


class AccountDeleteView(DeleteView):
    model = User
    context_object_name = "target_user"
    success_url = reverse_lazy("main:main")
    template_name = "main/delete.html"


class ProfileCreateView(CreateView):
    model = main_models.Profile
    context_object_name = "target_profile"
    form_class = main_forms.ProfileCreationForm
    success_url = reverse_lazy("main:main")
    template_name = "main/account_profile.html"

    def form_valid(self, form):
        temp_profile = form.save(commit=False)
        temp_profile.user = self.request.user
        temp_profile.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("main:account", kwargs={"pk": self.object.user.pk})


def upload_profile_picture(request):
    if request.method == "POST":
        form = main_forms.UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = form.save()
            # 성공적으로 저장되었을 때의 동작 등 추가 작업 수행

            return redirect("profile")  # 프로필 페이지 등으로 리디렉션

    else:
        form = main_forms.UserProfileForm()

    return render(request, "upload_profile.html", {"form": form})


@method_decorator(main_decorators.profile_ownership_required, "get")
@method_decorator(main_decorators.profile_ownership_required, "post")
class ProfileUpdateView(UpdateView):
    model = main_models.Profile
    context_object_name = "target_profile"
    form_class = main_forms.ProfileCreationForm
    success_url = reverse_lazy("main:main")
    template_name = "main/update_profile.html"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if "delete_image" in request.POST:
            profile = get_object_or_404(main_models.Profile, pk=kwargs["pk"])
            profile.image = None  # Set the image field to None
            profile.save()
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("main:account", kwargs={"pk": self.object.user.pk})


def admin_secret_key(request):
    if request.method == "POST" and "admin_secret_key" in request.POST:
        admin_secret_key = request.POST.get("admin_secret_key")
        admin_secret_key_original = "lglabelingsecret"
        if admin_secret_key == admin_secret_key_original:
            User.objects.filter(pk=request.user.pk).update(is_staff=1)
        else:
            return render(request, "main/admin.html", {"message": "비밀번호가 틀렸습니다."})
        return render(request, "main/admin.html", {"message": "admin계정으로 등록되었습니다."})
    return render(request, "main/admin.html")


def information(request):
    return render(request, "main/information.html")