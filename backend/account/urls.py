from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import Token,SignupView,ProfileView, verify_account, NotificationViewSet

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet)

urlpatterns=[
    path('signin/', Token.as_view(), name='SignIn'),
    path('signup/', SignupView.as_view(), name='SignUp'),
    path('profile/', ProfileView.as_view(), name='Profile'),
    path('verify_account/<str:uidb64>/<str:token>/', verify_account, name='verify_account'),
    path('', include(router.urls)),
]