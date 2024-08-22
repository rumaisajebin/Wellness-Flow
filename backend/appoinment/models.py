from django.db import models
from django.core.exceptions import ValidationError
from account.models import CustomUser

class DoctorSchedule(models.Model):
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'doctor'})
    day = models.CharField(max_length=10, choices=[
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()
    max_patients = models.IntegerField(default=12)

    def __str__(self):
        return f'{self.doctor.username} - {self.day} ({self.start_time} - {self.end_time})'

class Booking(models.Model):
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    )
    
    CONSULTATION_TYPE_CHOICES = (
        ('new_consultation', 'New Consultation'),
        ('prescription', 'Prescription Request'),
        ('follow_up', 'Follow-up Appointment'),
    )
        
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='patient_bookings', limit_choices_to={'role': 'patient'})
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='doctor_bookings', limit_choices_to={'role': 'doctor'})
    schedule = models.ForeignKey(DoctorSchedule, on_delete=models.CASCADE)
    schedule_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    consultation_type = models.CharField(max_length=30, choices=CONSULTATION_TYPE_CHOICES, default='new_consultation')
    confirmation_required = models.BooleanField(default=True)  # Indicates if the booking is pending confirmation
    booking_time = models.DateTimeField(auto_now_add=True)

    # def save(self, *args, **kwargs):
    #     # Ensure that the user associated with the patient profile is actually a patient
    #     if self.patient.role != 'patient':
    #         raise ValidationError("Only patients can make bookings.")
        
    #     # Ensure that the user associated with the doctor profile is actually a doctor
    #     if self.doctor.role != 'doctor':
    #         raise ValidationError("The selected user for doctor is not a doctor.")
        
    #     super().save(*args, **kwargs)

    def __str__(self):
        return f'Booking by {self.patient.username} with {self.doctor.username} on {self.schedule.day}'
