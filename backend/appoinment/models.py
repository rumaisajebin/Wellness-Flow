from django.db import models
from account.models import CustomUser
from datetime import datetime, timedelta
from django.utils import timezone

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

    def can_cancel(self, user):
        # Compare only the schedule date with today's date
        today = timezone.localdate()  # Get the current date
        
        # Allow doctor to cancel before confirming the booking
        if user.role == 'doctor' and self.status == 'pending':
            return True
        
        # Allow patient to cancel if today's date is before the consulting date
        if user.role == 'patient' and self.status == 'confirmed':
            return today < self.schedule_date
        
        return False
    
    def __str__(self):
        return f'Booking by {self.patient.username} with {self.doctor.username} on {self.schedule.day}'
