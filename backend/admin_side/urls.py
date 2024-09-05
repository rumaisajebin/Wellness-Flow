from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DoctorView,PatientView,BookingViewSet,AgreementViewSet

router = DefaultRouter()
router.register(r'doctors', DoctorView, basename='doctor')
router.register(r'patients', PatientView, basename='patient')
router.register(r'admin-booking', BookingViewSet, basename='admin-booking')
router.register(r'agreements', AgreementViewSet, basename='agreement')

urlpatterns = [
    path('', include(router.urls)),
]
