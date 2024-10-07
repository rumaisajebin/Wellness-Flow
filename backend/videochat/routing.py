from django.urls import re_path
from .consumer import VideoCallConsumer

video_websocket_urlpatterns = [
    re_path(r'^ws/video-call/(?P<room_name>[\w_]+)/$', VideoCallConsumer.as_asgi()),
]
