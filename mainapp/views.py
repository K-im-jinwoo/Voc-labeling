from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponseForbidden
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, DetailView

from mainapp.forms import ProfileCreationForm
from mainapp.models import Profile, Category, Review, FirstLabeledData


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


# sort를 기준으로 정렬해주는 함수
def sorting(sort, category_detail_list, positive, negative, neutral, everything):
    standard = []
    if sort == "positive":
        standard = positive
    elif sort == "negative":
        standard = negative
    elif sort == "neutral":
        standard = neutral
    elif sort == "everything":
        standard = everything

    # 오름차순 정렬
    for i in range(1, len(standard)):
        for j in range(i, 0, -1):
            if standard[j - 1].count() < standard[j].count():
                category_detail_list[j - 1], category_detail_list[j] = category_detail_list[j], category_detail_list[
                    j - 1]
                positive[j - 1], positive[j] = positive[j], positive[j - 1]
                negative[j - 1], negative[j] = negative[j], negative[j - 1]
                neutral[j - 1], neutral[j] = neutral[j], neutral[j - 1]
                everything[j - 1], everything[j] = everything[j], everything[j - 1]


def workstatus(request):
    try:

        # reqeust한 URL의 파라미터에 제품군, 시작위치, 끝 위치가 있으면 데이터를 반환함
        if 'category_product' in request.GET:
            # 청소기, 냉장고, 식기세척기 제품군 선택 시에만 수행
            if request.GET['category_product'] in ['cleaner', 'refrigerator', 'dish_washer']:

                # 해당 제품군의 카테고리 정보 불러옴
                category_product = request.GET['category_product']
                category_detail = Category.objects.filter(category_product=category_product)

                '''카테고리별 긍정 부정 개수'''
                # 긍정, 부정, 중립, 모두를 가져옴
                category_detail_list = []
                positive = []
                negative = []
                neutral = []
                everything = []

                for category in category_detail:
                    positive_temp = FirstLabeledData.objects.filter(category_id=category,
                                                                    first_labeled_emotion='positive')
                    negative_temp = FirstLabeledData.objects.filter(category_id=category,
                                                                    first_labeled_emotion='negative')
                    neutral_temp = FirstLabeledData.objects.filter(category_id=category,
                                                                   first_labeled_emotion='neutral')
                    everything_temp = FirstLabeledData.objects.filter(category_id=category)

                    category_detail_list.append(category.category_middle)
                    positive.append(positive_temp)
                    negative.append(negative_temp)
                    neutral.append(neutral_temp)
                    everything.append(everything_temp)

                if request.method == "POST" and 'sort' in request.POST:
                    sort = request.POST.get('sort')
                    sorting(sort, category_detail_list, positive, negative, neutral, everything)

                context = {'category_detail_list': category_detail_list, 'positive': positive, 'negative': negative,
                           'neutral': neutral, 'everything': everything}

                return render(request, 'mainapp/workstatus.html', context)
            return render(request, 'mainapp/workstatus.html')


        else:
            context = {'message': '제품을 다시 선택해주세요.'}
            return render(request, 'mainapp/workstatus.html', context)

    # 예외처리
    except Exception as identifier:
        print(identifier)

    return render(request, 'mainapp/workstatus.html')
