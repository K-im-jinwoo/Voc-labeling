from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include
from django.views.generic import TemplateView

from mainapp.views import AccountCreateView, AccountDetailView, ProfileCreateView

app_name = 'mainapp'

urlpatterns = [
    path('', TemplateView.as_view(template_name="mainapp/main_page.html"), name='main'),
    path('signup/', AccountCreateView.as_view(), name='signup'),
    path('login/', LoginView.as_view(template_name='mainapp/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('account/<int:pk>', AccountDetailView.as_view(), name='account'),
    path('account_profile/', ProfileCreateView.as_view(), name="account_profile")
]
