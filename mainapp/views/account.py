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
from django.shortcuts import get_object_or_404

from mainapp.models import Review
from ..forms import UserProfileForm
from django.shortcuts import render, redirect


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


def upload_profile_picture(request):
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = form.save()
            # 성공적으로 저장되었을 때의 동작 등 추가 작업 수행

            return redirect("profile")  # 프로필 페이지 등으로 리디렉션

    else:
        form = UserProfileForm()

    return render(request, "upload_profile.html", {"form": form})


@method_decorator(profile_ownership_required, "get")
@method_decorator(profile_ownership_required, "post")
class ProfileUpdateView(UpdateView):
    model = Profile
    context_object_name = "target_profile"
    form_class = ProfileCreationForm
    success_url = reverse_lazy("mainapp:main")
    template_name = "mainapp/update_profile.html"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if "delete_image" in request.POST:
            profile = get_object_or_404(Profile, pk=kwargs["pk"])
            profile.image = None  # Set the image field to None
            profile.save()
        return super().post(request, *args, **kwargs)

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
    # 제품별 모델개수
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

    sorted_products = sorted(product_model_counts, key=lambda x: x["category_product"])
    context["product_model_counts"] = sorted_products[:5]

    # 제품별 리뷰 총 개수
    category_review_counts = Review.objects.values("category_product").annotate(
        review_count=Count("review_content")
    )
    category_review_counts_labeled = (
        Review.objects.filter(labeled_user_id__isnull=False)
        .values("category_product")
        .annotate(labeled_count=Count("review_content"))
    )

    result_list = []

    for item in category_review_counts:
        matched_item = next(
            (
                x
                for x in category_review_counts_labeled
                if x["category_product"] == item["category_product"]
            ),
            None,
        )
        labeled_count = matched_item["labeled_count"] if matched_item else 0
        percentage_labeled = (
            round((labeled_count / item["review_count"]) * 100)
            if item["review_count"] > 0
            else 0
        )

        result_list.append(
            {
                "category_product": item["category_product"],
                "total_reviews": item["review_count"],
                "labeled_count": labeled_count,
                "percentage_labeled": percentage_labeled,
            }
        )

    sorted_result_list = sorted(result_list, key=lambda x: x["category_product"])
    context["result"] = sorted_result_list[:5]

    # 메인 첫번째
    temp_user = User.objects.all()
    # temp_user = User.objects.filter(is_superuser=False)
    result_name = []
    result_count = []
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
    user_ratios = []

    for user in users_with_review_counts:
        user_name.append(user.username)
        user_result_count.append(user.review_count)
        user_ratio_percentage = int((user.review_count / review_count) * 100)
        user_ratios.append(user_ratio_percentage)
        result = zip(user_name, user_result_count, user_ratios)

    result = sorted(result, key=lambda x: x[1], reverse=True)
    context["result_list"] = result

    return render(request, "mainapp/main_page.html", context)
