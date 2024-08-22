from rest_framework import serializers
from account.models import CustomUser,PatientProfile,DoctorProfile
from appoinment.models import DoctorSchedule

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email','role','username']
        

class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = PatientProfile
        exclude = []
        read_only_fields = ['user']
        
class DoctorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = DoctorProfile
        fields = [
            'id', 'user', 'profile_pic', 'full_name', 'phone_number', 'address', 
            'bio', 'medical_license_no', 'specialization', 'graduation_year', 
            'years_of_experience', 'workplace_name', 'medical_license_certificate', 
            'identification_document', 'certificates_degrees', 'curriculum_vitae', 
            'proof_of_work', 'specialization_certificates', 'is_profile_verify'
        ]        

class DoctorScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorSchedule
        fields = ['id', 'day', 'start_time', 'end_time', 'max_patients']        