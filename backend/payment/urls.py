# urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentView

router = DefaultRouter()
router.register(r'payments', PaymentView, basename='payment')  # Use a lowercase and plural name for consistency

urlpatterns = [
    path('', include(router.urls)),
]
