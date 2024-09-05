from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .serializers import DoctorSerializer, DoctorUpdateSerializer,PatientSerializer ,Booking ,BookingSerializer ,Agreement,AgreementSerializer
from account.models import DoctorProfile,PatientProfile
from io import BytesIO
from zipfile import ZipFile
import requests
from django.http import HttpResponse

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
    
    @action(detail=True, methods=['get'], url_path='download-certificates')
    def download_certificates(self, request, pk=None):
        doctor = get_object_or_404(DoctorProfile, pk=pk)
        certificates = {
            'medical_license_certificate': doctor.medical_license_certificate,
            'identification_document': doctor.identification_document,
            'certificates_degrees': doctor.certificates_degrees,
            'curriculum_vitae': doctor.curriculum_vitae,
            'proof_of_work': doctor.proof_of_work,
            'specialization_certificates': doctor.specialization_certificates,
        }

        # Create a ZIP file
        zip_buffer = BytesIO()
        with ZipFile(zip_buffer, 'w') as zip_file:
            for cert_name, cert_url in certificates.items():
                if cert_url:
                    response = requests.get(cert_url)
                    file_name = f"{cert_name}.pdf"  # Adjust file extension as needed
                    zip_file.writestr(file_name, response.content)
        
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename=certificates_{doctor.id}.zip'
        return response


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
    

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]    



class AgreementViewSet(viewsets.ModelViewSet):
    queryset = Agreement.objects.all()
    serializer_class = AgreementSerializer

    def create(self, request, *args, **kwargs):
        doctor_id = request.data.get('doctor')
        admin_id = request.data.get('admin')

        # Check if doctor and admin profiles exist
        if not doctor_id or not admin_id:
            return Response({'error': 'Doctor and Admin must be provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            agreement = Agreement.objects.create(
                doctor_id=doctor_id,
                admin_id=admin_id,
                start_date=request.data.get('start_date'),
                status='active'
            )
            serializer = self.get_serializer(agreement)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        agreement = self.get_object()
        serializer = self.get_serializer(agreement)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        agreement = self.get_object()
        privacy_accepted = request.data.get('privacy_accepted')
        signed = request.data.get('signed')

        if privacy_accepted is not None:
            agreement.privacy_accepted = privacy_accepted
        if signed is not None:
            agreement.signed = signed

        agreement.save()
        serializer = self.get_serializer(agreement)
        return Response(serializer.data)