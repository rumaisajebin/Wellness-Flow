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

        day = data.get('day')
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        # Check for overlapping schedules
        overlapping_schedules = DoctorSchedule.objects.filter(
            doctor=doctor,
            day=day,
            start_time__lt=end_time,
            end_time__gt=start_time
        )

        if overlapping_schedules.exists():
            raise serializers.ValidationError("This schedule overlaps with an existing schedule.")

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
    
    patient_username = serializers.CharField(source='patient.username', read_only=True)  # Fetch patient's username
    patient_email = serializers.EmailField(source='patient.email', read_only=True)  # Fetch patient's email
    patient_full_name = serializers.CharField(source='patient.patient_profile.full_name', read_only=True)  # Fetch patient's full name
    
    # Add this field to expose the patient ID
    patient_id = serializers.IntegerField(source='patient.id', read_only=True)
    doctor_id = serializers.IntegerField(source='doctor.id', read_only=True)

    doctor = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(role='doctor'))
    schedule = serializers.PrimaryKeyRelatedField(queryset=DoctorSchedule.objects.all())
    patient = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Booking
        fields = [
            'id',
            'patient_id', 
            'doctor_id',
            'patient', 
            'patient_username', 
            'patient_email',
            'patient_full_name',
            'doctor', 
            'doctor_username', 
            'doctor_email', 
            'doctor_specialization', 
            'schedule', 
            'schedule_date', 
            'consultation_type', 
            'booking_time', 
            'confirmation_required', 
            'status',
            'paid'
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
            
            if data.get('status') == 'confirmed' and not data.get('paid', False):
                raise serializers.ValidationError("Booking cannot be confirmed until it is paid.")
        
        return data

    def create(self, validated_data):
        validated_data['patient'] = self.context['request'].user
        return super().create(validated_data)
