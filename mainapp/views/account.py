from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView
from mainapp.decorators import profile_ownership_required

from mainapp.forms import ProfileCreationForm, AccountUpdateForm
from mainapp.models import Profile, Category, Review
from django.db.models import Count, Q

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


def information(request):
    return render(request, 'mainapp/information.html')

def main_page(request):
    context = dict()

    # 제품별 모델개수
    product_names = Review.objects.values('category_product').distinct()
    product_model_counts = []
    for product in product_names:
        model_name_count = Review.objects.exclude(Q(model_name__isnull=True) | Q(model_name="")).filter(category_product=product['category_product']).values('model_name').distinct().count()
        product_model_counts.append({
            'category_product': product['category_product'],
            'model_name_count': model_name_count
        })
    
    sorted_products = sorted(product_model_counts, key=lambda x: x['category_product'])
    context['product_model_counts'] = sorted_products[:5]

    # 제품별 리뷰 총 개수
    category_review_counts = Review.objects.values('category_product').annotate(review_count=Count('review_content'))
    category_review_counts_first_true = Review.objects.filter(first_status=True).values('category_product').annotate(first_true_count=Count('review_content'))
    
    result_list = []
    
    for item in category_review_counts:
        matched_item = next((x for x in category_review_counts_first_true if x['category_product'] == item['category_product']), None)
        first_true_count = matched_item['first_true_count'] if matched_item else 0
        percentage_labelled = round((first_true_count / item['review_count']) * 100) if item['review_count'] > 0 else 0
        
        result_list.append({
            'category_product': item['category_product'],
            'total_reviews': item['review_count'],
            'first_status_True': first_true_count,
            'percentage_labelled': percentage_labelled,
            })
        
    sorted_result_list= sorted(result_list, key=lambda x: x['category_product'])
    context['result'] = sorted_result_list[:5]
        
    return render(request, 'mainapp/main_page.html', context)


