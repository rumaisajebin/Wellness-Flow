from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import DoctorSerializer,DoctorProfile

class DoctorProfileViewSet(viewsets.ModelViewSet):
    queryset = DoctorProfile.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DoctorProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

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


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def block_profile(request, pk):
    instance = get_object_or_404(DoctorProfile, pk=pk)
    if not instance.is_block:
        instance.is_block = True
        instance.save()
    
    response_data = {
        "status": 200,        
        "title": "Successfully Blocked",
        "message": "Doctor Profile Successfully blocked.", 
        "redirect": "true",       
        "redirect_url": reverse('doctor-profile-list-create')
    }
    return Response(response_data)

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def verify_profile(request, pk):
    instance = get_object_or_404(DoctorProfile, pk=pk)
    if not instance.is_verify:
        instance.is_verify = True
        instance.save()
    
    response_data = {
        "status": 200,        
        "title": "Successfully Verified",
        "message": "Doctor Profile Successfully verified.", 
        "redirect": "true",       
        "redirect_url": reverse('doctor-profile-list-create')
    }
    return Response(response_data)
