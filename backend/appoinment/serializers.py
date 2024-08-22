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


    def validate(self, data):
        request = self.context['request']
        # if request.user.role == 'doctor':
        #     raise serializers.ValidationError("Only patients can make bookings.")
        doctor = data.get('doctor')
        print(doctor)
        schedule_date = data.get('schedule_date')
        existing_bookings = Booking.objects.filter(
            patient__id=request.user.id,
            doctor=doctor,
            schedule_date=schedule_date
        )
        if existing_bookings.exists():
            raise serializers.ValidationError("Slot is already booked.")
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['patient'] = user
        return super().create(validated_data)