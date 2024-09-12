from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DoctorProfileViewSet,TransactionViewSet

router = DefaultRouter()
router.register(r'doctor-profiles', DoctorProfileViewSet, basename='doctor-profile')
router.register(r'transactions', TransactionViewSet, basename='transaction')

urlpatterns = [
    path('', include(router.urls)),
]
