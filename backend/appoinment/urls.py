from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DoctorScheduleViewSet,BookingViewSet

router = DefaultRouter()
router.register(r'DoctorSchedule', DoctorScheduleViewSet)
router.register(r'bookings', BookingViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
