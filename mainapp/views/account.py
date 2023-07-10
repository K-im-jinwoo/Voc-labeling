from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView
from mainapp.decorators import profile_ownership_required

from mainapp.forms import ProfileCreationForm, AccountUpdateForm
from mainapp.models import Profile

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView


class AccountCreateView(CreateView):
    model = User
    form_class = UserCreationForm  # 기본적인 userform을 제공해준다.
    success_url = reverse_lazy('mainapp:login')  # reverse는 함수형, reverse_lazy는 class에서 사욯한다.
    template_name = 'mainapp/signup.html'

class AccountLoginView(LoginView):
    form_class = AuthenticationForm
    template_name = 'mainapp/login.html'


class AccountDetailView(DetailView):
    model = User
    context_object_name = 'target_user'
    template_name = 'mainapp/account.html'

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated and self.get_object() == self.request.user:
            return super().get(*args, **kwargs)
        else:
            return HttpResponseForbidden()

    def post(self, *args, **kwargs):
        if self.request.user.is_authenticated and self.get_object() == self.request.user:
            return super().get(*args, **kwargs)
        else:
            return HttpResponseForbidden()


class AccountUpdateView(UpdateView):
    model = User
    context_object_name = 'target_user'
    form_class = AccountUpdateForm
    success_url = reverse_lazy('mainapp:main')
    template_name = 'mainapp/update.html'


class AccountDeleteView(DeleteView):
    model = User
    context_object_name = 'target_user'
    success_url = reverse_lazy('mainapp:main')
    template_name = 'mainapp/delete.html'


class ProfileCreateView(CreateView):
    model = Profile
    context_object_name = 'target_profile'
    form_class = ProfileCreationForm
    success_url = reverse_lazy('mainapp:main')
    template_name = 'mainapp/account_profile.html'

    def form_valid(self, form):
        temp_profile = form.save(commit=False)
        temp_profile.user = self.request.user
        temp_profile.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('mainapp:account', kwargs={'pk': self.object.user.pk})


@method_decorator(profile_ownership_required, 'get')
@method_decorator(profile_ownership_required, 'post')
class ProfileUpdateView(UpdateView):
    model = Profile
    context_object_name = 'target_profile'
    form_class = ProfileCreationForm
    success_url = reverse_lazy('mainapp:main')
    template_name = 'mainapp/update_profile.html'

    def get_success_url(self):
        return reverse('mainapp:account', kwargs={'pk': self.object.user.pk})


def admin_secret_key(request):
    if request.method == "POST" and 'admin_secret_key' in request.POST:
        admin_secret_key = request.POST.get('admin_secret_key')
        admin_secret_key_original = "lglabelingsecret"
        if admin_secret_key == admin_secret_key_original:
            User.objects.filter(pk=request.user.pk).update(is_staff=1)
        else:
            return render(request, 'mainapp/admin.html', {'message': '비밀번호가 틀렸습니다.'})
        return render(request, 'mainapp/admin.html', {'message': 'admin계정으로 등록되었습니다.'})
    return render(request, 'mainapp/admin.html')
