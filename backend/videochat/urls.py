from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VideoTokenViewSet

router = DefaultRouter()
router.register(r'video-token', VideoTokenViewSet, basename='video-token')
# router.register(r'video-invite', VideoInviteViewSet, basename='video-invite')
# path('send-sms/', SendSMSView.as_view(), name='send_sms'),

urlpatterns = [
    path('', include(router.urls)),
]
