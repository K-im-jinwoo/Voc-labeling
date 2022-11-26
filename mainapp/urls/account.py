from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from mainapp.views.account import AccountCreateView, AccountDetailView, ProfileCreateView

patterns = [
    path('login/', LoginView.as_view(template_name='mainapp/login.html'), name='login'),
    path('signup/', AccountCreateView.as_view(), name='signup'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('account/<int:pk>', AccountDetailView.as_view(), name='account'),
    path('account_profile/', ProfileCreateView.as_view(), name="account_profile"),
]
