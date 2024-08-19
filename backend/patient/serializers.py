from rest_framework import serializers
from account.models import CustomUser,PatientProfile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email','role','username']
        

class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = PatientProfile
        exclude = []
        read_only_fields = ['user']
        