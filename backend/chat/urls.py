
# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .views import ChatMessageViewSet

# router = DefaultRouter()
# router.register(r'chat/(?P<room_name>[^/.]+)', ChatMessageViewSet, basename='chat-messages')

# urlpatterns = [
#     # path('', include(router.urls)),
# ]

# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MessageViewSet,SendMessage

router = DefaultRouter()
router.register(r'messages', MessageViewSet, basename='messages')

urlpatterns = [
    path('', include(router.urls)),
    path('messages/<str:room_name>/', MessageViewSet.as_view({'get': 'list'}), name='fetch_messages'),
    path('send-message/', SendMessage.as_view(), name='send_message'),
]
