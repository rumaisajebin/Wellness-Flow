# views.py
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import VideoCallSession
from .serializers import VideoCallSessionSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class VideoTokenViewSet(viewsets.ModelViewSet):
    queryset = VideoCallSession.objects.all().order_by("-created_on")
    serializer_class = VideoCallSessionSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save()
        self.notify_group(serializer.instance.appointment.id, 'created')

    def perform_update(self, serializer):
        serializer.save()
        self.notify_group(serializer.instance.appointment.id, 'updated')

    def destroy(self, request, pk=None):
        room = get_object_or_404(VideoCallSession, id=pk)
        authenticate_class = JWTAuthentication()
        user, _ = authenticate_class.authenticate(request)

        if room and user and user.id == room.appointment.user.id:
            room.delete()
            self.notify_group(room.appointment.id, 'deleted')
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {"message": "Unauthorized."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    def notify_group(self, appointment_id, action):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"video_call_{appointment_id}",
            {
                "type": "video_message",
                "message": {
                    "action": action,
                    "appointment_id": appointment_id
                }
            }
        )
