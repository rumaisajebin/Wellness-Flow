from rest_framework import serializers
from account.models import CustomUser,DoctorProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email','role','username']
        

class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = DoctorProfile
        exclude = ['is_profile_verify','rejection_reason']
        read_only_fields = ['user']