from django.urls import path
from .views import Token,SignupView,ProfileView

urlpatterns=[
    path('/signin', Token.as_view(), name='SignIn'),
    path('/signup', SignupView.as_view(), name='SignUp'),
    path('/profile', ProfileView.as_view(), name='Profile'),
]