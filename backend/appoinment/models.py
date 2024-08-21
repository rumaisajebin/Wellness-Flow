from django.db import models
from account.models import CustomUser,DoctorProfile
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError


DAYS_OF_WEEK = [
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
    ('Saturday', 'Saturday'),
    ('Sunday', 'Sunday'),
]


class DoctorSchedule(models.Model):
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK) 
    start_time = models.TimeField()  
    end_time = models.TimeField() 
    max_patients = models.IntegerField(default=12)  

@receiver(post_save, sender=DoctorProfile)
def create_default_schedule(sender, instance, **kwargs):
    if instance.is_profile_verify == 'approved':
        default_schedule = {
            'Monday': ('15:00', '20:00'),
            'Tuesday': ('15:00', '20:00'),
            'Wednesday': ('15:00', '20:00'),
            'Thursday': ('15:00', '20:00'),
            'Friday': ('15:00', '20:00'),
            'Saturday': ('10:00', '14:00'),
            'Sunday': ('10:00', '14:00'),
        }
        
        for day, times in default_schedule.items():
            DoctorSchedule.objects.create(
                doctor=instance.user,
                day=day,
                start_time=times[0],
                end_time=times[1],
            )


class Booking(models.Model):
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='patient_bookings')
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='doctor_bookings')
    schedule = models.ForeignKey(DoctorSchedule, on_delete=models.CASCADE)
    booking_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('confirmed', 'Confirmed')], default='pending')

    def save(self, *args, **kwargs):
        # Ensure that the user associated with the patient profile is not a doctor
        if self.patient.user.is_doctor:
            raise ValidationError("Only patients can make bookings.")
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f'Booking by {self.patient.username} with {self.doctor.username} on {self.schedule.day}'