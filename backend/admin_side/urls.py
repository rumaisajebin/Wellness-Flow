from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DoctorView,PatientView

router = DefaultRouter()
router.register(r'doctors', DoctorView, basename='doctor')
router.register(r'patients', PatientView, basename='patient')

urlpatterns = [
    path('', include(router.urls)),
]
