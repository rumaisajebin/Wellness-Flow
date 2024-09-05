from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .models import DoctorSchedule, Booking
from rest_framework import serializers
from .models import DoctorSchedule, Booking, CustomUser

class DoctorScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorSchedule
        fields = ['id', 'doctor', 'day', 'start_time', 'end_time', 'max_patients']

    def validate(self, data):
        doctor = data['doctor']
        if doctor.role != 'doctor':
            raise serializers.ValidationError("Only doctors can create schedules.")
        if doctor.doctor_profile.is_profile_verify != 'approved':
            raise serializers.ValidationError("Your profile is not verified. You cannot create a schedule.")
        return data

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
    doctor_username = serializers.CharField(source='doctor.username', read_only=True)
    doctor_email = serializers.CharField(source='doctor.email', read_only=True)
    doctor_specialization = serializers.CharField(source='doctor.doctor_profile.specialization', read_only=True)
    # patient_username = serializers.CharField(source='patient.username', read_only=True)  
    
    doctor = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(role='doctor'))
    schedule = serializers.PrimaryKeyRelatedField(queryset=DoctorSchedule.objects.all())
    patient = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Booking
        fields = [
            'id',
            'patient', 
            # 'patient_username',
            'doctor', 
            'doctor_username', 
            'doctor_email', 
            'doctor_specialization', 
            'schedule', 
            'schedule_date', 
            'consultation_type', 
            'booking_time', 
            'confirmation_required', 
            'status'
        ]
        read_only_fields = ['patient', 'booking_time', 'confirmation_required']

    def validate(self, data):
        request = self.context['request']
        doctor = data.get('doctor')
        schedule = data.get('schedule')
        schedule_date = data.get('schedule_date')
        
        if schedule:
            if Booking.objects.filter(
                patient=request.user, doctor=doctor, schedule_date=schedule_date
            ).exclude(status='canceled').exists():
                raise serializers.ValidationError("You have already booked this slot.")
            
            if not DoctorSchedule.objects.filter(id=schedule.id, day=schedule.day).exists():
                raise serializers.ValidationError("This slot is unavailable for booking.")
        
        return data

    def create(self, validated_data):
        validated_data['patient'] = self.context['request'].user
        return super().create(validated_data)