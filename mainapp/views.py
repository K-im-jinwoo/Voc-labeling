from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponseForbidden
from django.urls import reverse_lazy
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


def type_to_variable(type, positive, negative, neutral, everything):
    if type == 'positive':
        variable = positive
    elif type == 'negative':
        variable = negative
    elif type == 'neutral':
        variable = neutral
    elif type == 'everything':
        variable = everything
    return variable


# sort를 기준으로 정렬해주는 함수(삽입정렬)
def sorting(sort, category_detail_list, positive, negative, neutral, everything):
    standard = []

    standard = type_to_variable(sort, positive, negative, neutral, everything)

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
                alltotal = Review.objects.filter(category_product=category_product).count()
                first_num = Review.objects.filter(category_product=category_product).filter(first_status=True).count()
                second_num = Review.objects.filter(category_product=category_product).filter(second_status=True).count()
                dummy_num = Review.objects.filter(category_product=category_product).filter(dummy_status=True).count()

                '''카테고리별 긍정 부정 개수'''
                context = {}
                category_detail_list = []
                positive = []
                negative = []
                neutral = []
                everything = []
                order = []
                i = 0

                # 카테고리별 라벨링된 데이터 개수 불러옴(개수 아니기 때문에 바로 쓰시면 됩니다.)
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
                    order.append(i)
                    i += 1

                # 정렬 요청 들어오면 session에 정렬 요구 상태 저장
                if request.method == "POST" and 'sort' in request.POST:
                    sort = request.POST.get('sort')
                    request.session['sort'] = sort

                # session에 저장한 요구 상태를 읽어 정렬 수행
                if request.session['sort']:
                    sorting(request.session['sort'], category_detail_list, positive, negative, neutral, everything)

                # 번호 개수를 눌렀을 때 (대상, 현상)과 원문데이터 보여줌
                if request.method == "GET" and 'showing_index' in request.GET:
                    # 번호의 위치(showing_index)와 번호의 긍부정 여부(showing_type)을 가져옴
                    showing_index = request.GET.get('showing_index')
                    showing_type = request.GET.get('showing_type')

                    # labeled_word에 대상 - 현상 키워드 쌍을 저장함
                    labeled_word = type_to_variable(showing_type, positive, negative, neutral, everything)
                    labeled_word = labeled_word[int(showing_index)]
                    context['labeled_word'] = labeled_word

                    # 번호 눌렀을 때 리뷰 원문 데이터 보여주기
                    labeled_review = labeled_word.values_list('review_id', flat=True)
                    labeled_review = Review.objects.filter(pk__in=labeled_review)
                    context['labeled_review'] = labeled_review

                data = zip(category_detail_list, positive, negative, neutral, everything, order)

                context['data'] = data
                context['category_product'] = category_product
                context['alltotal'] = alltotal
                context['first_num'] = first_num
                context['dummy_num'] = dummy_num
                context['second_num'] = second_num
                return render(request, 'mainapp/workstatus.html', context=context)
            return render(request, 'mainapp/workstatus.html')


        else:
            context = {'message': '제품을 다시 선택해주세요.'}
            return render(request, 'mainapp/workstatus.html', context)

    # 예외처리
    except Exception as identifier:
        print(identifier)

    return render(request, 'mainapp/workstatus.html')
