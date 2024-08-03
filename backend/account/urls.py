from django.urls import path
from .views import Token,SignupView,ProfileView,verify_account

urlpatterns=[
    path('signin/', Token.as_view(), name='SignIn'),
    path('signup/', SignupView.as_view(), name='SignUp'),
    path('profile/', ProfileView.as_view(), name='Profile'),
    path('verify_account/<str:uidb64>/<str:token>/', verify_account, name='verify_account'),
]