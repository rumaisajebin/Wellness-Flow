from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import  PatientSerializer,PatientProfile
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import ValidationError

class PatientProfileViewSet(viewsets.ModelViewSet):
    queryset = PatientProfile.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        if self.request.user.is_staff:
            return PatientProfile.objects.all()
        return PatientProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        try:
            serializer.save()
        except ValidationError as e:
            print(e.detail)  # Log validation errors
            raise e

    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)')
    def get_by_user_id(self, request, user_id=None):
        profile = get_object_or_404(PatientProfile, user__id=user_id)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='profile-id')
    def get_profile_id(self, request):
        user = request.user
        profile = get_object_or_404(PatientProfile, user=user)
        return Response({"profile_id": profile.id})
