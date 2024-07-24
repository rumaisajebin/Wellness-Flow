from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DoctorProfileViewSet, block_profile, verify_profile

router = DefaultRouter()
router.register(r'doctor-profiles', DoctorProfileViewSet, basename='doctor-profile')

urlpatterns = [
    path('', include(router.urls)),
    path('doctor-profiles/<int:pk>/block/', block_profile, name='doctor-profile-block'),
    path('doctor-profiles/<int:pk>/verify/', verify_profile, name='doctor-profile-verify'),
]
