from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PatientProfileViewSet, DoctorProfileViewSet, TransactionViewSet


router = DefaultRouter()
router.register(r'patient-profiles', PatientProfileViewSet, basename='patient-profile')
router.register(r'doctor-profiles', DoctorProfileViewSet, basename='doctor-profile')
router.register(r'transactions', TransactionViewSet, basename='transaction-history')

urlpatterns = [
    path('', include(router.urls)),
]
