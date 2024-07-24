from rest_framework import serializers
from account.models import CustomUser,DoctorProfile

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorProfile
        exclude = ['is_verify','is_block']
        read_only_fields = ['user']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email','role']
        
