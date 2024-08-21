from rest_framework import serializers
from .models import DoctorSchedule,Booking

class DoctorScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorSchedule
        fields = ['id', 'doctor', 'day', 'start_time', 'end_time', 'max_patients']

    def validate(self, data):
        doctor = data['doctor']

        # Check if the user is a doctor
        if doctor.role != 'doctor':
            raise serializers.ValidationError("Only doctors can create schedules.")

        # Check if the doctor's profile is verified
        if doctor.doctor_profile.is_profile_verify != 'approved':
            raise serializers.ValidationError("Your profile is not verified. You cannot create a schedule.")

        return data


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['patient', 'doctor', 'schedule', 'slot_time', 'booking_time']
        read_only_fields = ['patient', 'booking_time']

    def validate(self, data):
        request = self.context['request']
        if request.user.is_doctor:
            raise serializers.ValidationError("Only patients can make bookings.")
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        patient_profile = patient_profile.objects.get(user=user)
        validated_data['patient'] = patient_profile
        return super().create(validated_data)
