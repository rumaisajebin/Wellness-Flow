from rest_framework import serializers
from account.models import CustomUser, DoctorProfile,PatientProfile

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