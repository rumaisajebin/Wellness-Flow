from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .serializers import DoctorSerializer, DoctorUpdateSerializer,PatientSerializer
from account.models import DoctorProfile,PatientProfile

class DoctorView(viewsets.ModelViewSet):
    queryset = DoctorProfile.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return DoctorUpdateSerializer
        return DoctorSerializer

    @action(detail=True, methods=['post'], url_path='verify')
    def verify_doctor(self, request, pk=None):
        doctor = get_object_or_404(DoctorProfile, pk=pk)
        status_choice = request.data.get('status')
        rejection_reason = request.data.get('reason', '')
        print("check",rejection_reason)
        if status_choice in ['approved', 'denied']:
            doctor.is_profile_verify = status_choice
            doctor.rejection_reason = rejection_reason if status_choice == 'denied' else ''
            doctor.save()
            status_message = f"Doctor {status_choice}"
            return Response({"status": status_message}, status=status.HTTP_200_OK)
        
        return Response({"error": "Invalid status choice"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='block')
    def block_doctor(self, request, pk=None):
        doctor = get_object_or_404(DoctorProfile, pk=pk)
        action = request.data.get('action')

        if action == 'block':
            doctor.user.is_active = False  # Block the doctor
            status_message = "Doctor blocked"
        elif action == 'unblock':
            doctor.user.is_active = True  # Unblock the doctor
            status_message = "Doctor unblocked"
        else:
            return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

        doctor.user.save()
        return Response({"status": status_message}, status=status.HTTP_200_OK)



    @action(detail=False, methods=['get'], url_path='verification-choices')
    def verification_choices(self, request):
        choices = dict(DoctorProfile.VERIFICATION_STATUS_CHOICES)
        return Response(choices, status=status.HTTP_200_OK)


class PatientView(viewsets.ModelViewSet):
    queryset = PatientProfile.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PatientProfile.objects.exclude(user__is_superuser=True) 
    
    @action(detail=True, methods=['post'], url_path='block-unblock')
    def block_unblock_patient(self, request, pk=None):
        patient = get_object_or_404(PatientProfile, pk=pk)
        action = request.data.get('action')

        if action == 'block':
            patient.user.is_active = False  # Block the patient
            status_message = "Patient blocked"
        elif action == 'unblock':
            patient.user.is_active = True  # Unblock the patient
            status_message = "Patient unblocked"
        else:
            return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

        patient.user.save()
        return Response({"status": status_message}, status=status.HTTP_200_OK)