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

    try:

        # reqeust한 URL의 파라미터에 제품군, 시작위치, 끝 위치가 있으면 데이터를 반환함
        if 'category_product' in request.GET:
            # 청소기, 냉장고, 식기세척기 제품군 선택 시에만 수행
            if request.GET['category_product'] in ['cleaner', 'refrigerator', 'dish_washer']:
                category_product = request.GET['category_product']
                # 해당 제품군의 카테고리 정보 불러옴
                category_detail = Category.objects.filter(category_product=category_product)
                # workstatus.html에 보낼 context 데이터
                context = {'category_detail': category_detail}
                return render(request, 'mainapp/workstatus.html', context)
            return render(request, 'mainapp/workstatuw.html')

        else:
            context = {'message': '제품을 다시 선택해주세요.'}
            return render(request, 'mainapp/workstatus.html', context)

    # 예외처리
    except Exception as identifier:
        print(identifier)

    return render(request, 'mainapp/workstatus.html')
