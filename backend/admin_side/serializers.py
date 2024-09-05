from rest_framework import serializers
from account.models import CustomUser, DoctorProfile,PatientProfile
from appoinment.models import Booking,DoctorSchedule
from .models import Agreement


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'role', 'username','is_active','is_verify']

class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    verification_status_choices = serializers.SerializerMethodField()

    class Meta:
        model = DoctorProfile
        fields = '__all__'  # Expose all fields of DoctorProfile including the new choices field

    def get_verification_status_choices(self, obj):
        return dict(DoctorProfile.VERIFICATION_STATUS_CHOICES)


class DoctorUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorProfile
        fields = ['is_profile_verify', 'rejection_reason'] 
        

class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only = True)
    class Meta:
        model = PatientProfile
        fields = '__all__' 

class DoctorScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorSchedule
        fields = ['id', 'doctor', 'day', 'start_time', 'end_time', 'max_patients']

class DoctorProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='doctor_profile.full_name')

    class Meta:
        model = CustomUser
        fields = ['full_name']

class PatientProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='patient_profile.full_name')

    class Meta:
        model = CustomUser
        fields = ['full_name']        
        
class BookingSerializer(serializers.ModelSerializer):
    doctor = DoctorProfileSerializer(read_only=True)
    patient = PatientProfileSerializer(read_only=True)
    schedule = DoctorScheduleSerializer(read_only=True)  # Updated to include the schedule details

    class Meta:
        model = Booking
        fields = [
            'id',
            'patient', 
            'doctor', 
            'schedule', 
            'schedule_date', 
            'consultation_type', 
            'booking_time', 
            'confirmation_required', 
            'status'
        ]
        read_only_fields = ['patient', 'booking_time', 'confirmation_required']

        
        
class AgreementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agreement
        fields = '__all__'        