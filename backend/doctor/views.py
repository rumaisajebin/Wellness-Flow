from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import DoctorSerializer,DoctorProfile
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import ValidationError

class DoctorProfileViewSet(viewsets.ModelViewSet):
    queryset = DoctorProfile.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser) 

    def get_queryset(self):
        if self.request.user.is_staff:
            return DoctorProfile.objects.all()
        return DoctorProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        try:
            print(serializer)
            serializer.save()
        except ValidationError as e:
            print(e.detail)  # Log validation errors
            raise e

    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)')
    def get_by_user_id(self, request, user_id=None):
        profile = get_object_or_404(DoctorProfile, user__id=user_id)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='profile-id')
    def get_profile_id(self, request):
        user = request.user
        profile = get_object_or_404(DoctorProfile, user=user)
        return Response({"profile_id": profile.id})
