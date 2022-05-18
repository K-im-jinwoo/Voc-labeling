from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponseForbidden
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, DetailView

from mainapp.forms import ProfileCreationForm
from mainapp.models import Profile, Category


class AccountCreateView(CreateView):
    model = User
    form_class = UserCreationForm  # 기본적인 userform을 제공해준다.
    success_url = reverse_lazy('mainapp:login')  # reverse는 함수형, reverse_lazy는 class에서 사욯한다.
    template_name = 'mainapp/signup.html'


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

def workstatus(request):
    if request.method == "GET":
        if 'category_product' == 'cleaner':
            status_category = Category.objects.filter(category_product='cleaner')
            context = {'status_category': status_category}
            return render(request, 'mainapp/workstatus.html', context)
        elif 'category_product' == 'refigerator':
            status_category = Category.objects.filter(category_product='refigerator')
            context = {'status_category': status_category}
            return render(request, 'mainapp/workstatus.html', context)
        else:
            status_category = Category.objects.filter(category_product='dish_washer')
            context = {'status_category': status_category}
            return render(request, 'mainapp/workstatus.html', context)


    #
    #     if 'category_product'  in ['cleaner', 'refrigerator', 'dish_washer']:
    #         category_product = request.GET['category_product']
    #         status_category = Category.objects.filter(category_product=category_product)
    #         context = {'status_category': status_category}
    #         return render(request, 'mainapp/workstatus.html', context)
    #     return render(request, 'mainapp/workstatus.html')
    # else:
    #     return render(request, 'mainapp/workstatus.html')


    return render(request, 'mainapp/workstatus.html')
