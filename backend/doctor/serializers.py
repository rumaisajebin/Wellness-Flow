from rest_framework import serializers
from account.models import CustomUser,DoctorProfile
from payment.models import Transaction,Booking


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email','role','username','wallet_balance']
        

class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = DoctorProfile
        exclude = ['is_profile_verify','rejection_reason']
        read_only_fields = ['user']
        
class BookingSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.username', read_only=True)
    doctor_name = serializers.CharField(source='doctor.username', read_only=True)
    class Meta:
        model = Booking
        fields = [
            'patient_name',
            'patient', 
            'doctor_name',
            'doctor', 
            'schedule', 
            'schedule_date', 
            'status', 
            'consultation_type', 
            'confirmation_required', 
            'booking_time', 
            'paid'
        ]

class TransactionSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.username', read_only=True)
    booking = BookingSerializer(read_only=True) 
    class Meta:
        model = Transaction
        fields = '__all__'