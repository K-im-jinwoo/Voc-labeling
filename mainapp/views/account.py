from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView
from mainapp.decorators import profile_ownership_required
from django.db.models import Count, Q
from mainapp.forms import ProfileCreationForm, AccountUpdateForm
from mainapp.models import Profile, Category, Review
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView


class AccountCreateView(CreateView):
    model = User
    form_class = UserCreationForm  # 기본적인 userform을 제공해준다.
    success_url = reverse_lazy(
        "mainapp:login"
    )  # reverse는 함수형, reverse_lazy는 class에서 사욯한다.
    template_name = "mainapp/signup.html"


class AccountLoginView(LoginView):
    form_class = AuthenticationForm
    template_name = "mainapp/login.html"


class AccountDetailView(DetailView):
    model = User
    context_object_name = "target_user"
    template_name = "mainapp/account.html"

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
    form_class = AccountUpdateForm
    success_url = reverse_lazy("mainapp:main")
    template_name = "mainapp/update.html"


class AccountDeleteView(DeleteView):
    model = User
    context_object_name = "target_user"
    success_url = reverse_lazy("mainapp:main")
    template_name = "mainapp/delete.html"


class ProfileCreateView(CreateView):
    model = Profile
    context_object_name = "target_profile"
    form_class = ProfileCreationForm
    success_url = reverse_lazy("mainapp:main")
    template_name = "mainapp/account_profile.html"

    def form_valid(self, form):
        temp_profile = form.save(commit=False)
        temp_profile.user = self.request.user
        temp_profile.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("mainapp:account", kwargs={"pk": self.object.user.pk})


@method_decorator(profile_ownership_required, "get")
@method_decorator(profile_ownership_required, "post")
class ProfileUpdateView(UpdateView):
    model = Profile
    context_object_name = "target_profile"
    form_class = ProfileCreationForm
    success_url = reverse_lazy("mainapp:main")
    template_name = "mainapp/update_profile.html"

    def get_success_url(self):
        return reverse("mainapp:account", kwargs={"pk": self.object.user.pk})


def admin_secret_key(request):
    if request.method == "POST" and "admin_secret_key" in request.POST:
        admin_secret_key = request.POST.get("admin_secret_key")
        admin_secret_key_original = "lglabelingsecret"
        if admin_secret_key == admin_secret_key_original:
            User.objects.filter(pk=request.user.pk).update(is_staff=1)
        else:
            return render(request, "mainapp/admin.html", {"message": "비밀번호가 틀렸습니다."})
        return render(request, "mainapp/admin.html", {"message": "admin계정으로 등록되었습니다."})
    return render(request, "mainapp/admin.html")


def information(request):
    return render(request, "mainapp/information.html")


def main_page(request):
    context = dict()
    product_names = Review.objects.values("category_product").distinct()
    product_model_counts = []

    for product in product_names:
        model_name_count = (
            Review.objects.exclude(Q(model_name__isnull=True) | Q(model_name=""))
            .filter(category_product=product["category_product"])
            .values("model_name")
            .distinct()
            .count()
        )
        product_model_counts.append(
            {
                "category_product": product["category_product"],
                "model_name_count": model_name_count,
            }
        )

    sorted_products = sorted(
        product_model_counts, key=lambda x: x["model_name_count"], reverse=True
    )
    context["product_model_counts"] = sorted_products[:5]

    # 메인 첫번째
    temp_user = User.objects.all()
    # temp_user = User.objects.filter(is_superuser=False)
    result_name = []
    result_count = []
    context = {}
    product_count = (
        Category.objects.values("category_product").distinct().count()
    )  # 제품갯수
    user_count = temp_user.count()  # 유저수
    review_count = Review.objects.count()  # 총리뷰수

    context["product_count"] = product_count
    context["user_count"] = user_count
    context["review_count"] = review_count

    users_with_review_counts = User.objects.annotate(
        review_count=Count("review")
    )  # 아이디당 리뷰 몇개달았는지 수

    total_review_count_by_users = 0  # 아이디당 리뷰 수 총 합
    for user in users_with_review_counts:
        total_review_count_by_users += user.review_count

    context["review_ratio"] = round(
        total_review_count_by_users / review_count, 1
    )  # 아이디당 리뷰 수 총합 / 총리뷰수


    # 메인 세번째
    user_name = []
    user_result_count = []
    user_ratio = round(
        total_review_count_by_users / review_count, 1
    )
    user_ratios = []

    for user in users_with_review_counts:
        user_name.append(user.username)
        user_result_count.append(user.review_count)
        user_ratios.append(user_ratio)
        result = zip(user_name, user_result_count,user_ratios)

    result = sorted(result, key=lambda x: x[1], reverse=True)
    context["result_list"] = result
    


    return render(request, "mainapp/main_page.html", context)
