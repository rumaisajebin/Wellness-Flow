from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import Slot, Booking,Time

router = DefaultRouter()
router.register(r'slots', Slot)
router.register(r'bookings', Booking)
router.register(r'time-slots', Time)

urlpatterns = [
    path('', include(router.urls)),
]
