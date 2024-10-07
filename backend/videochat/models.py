from django.db import models
from appoinment.models import Booking
# Create your models here.

class VideoCallSession(models.Model):
    appointment = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='video_session')
    video_start_time = models.TimeField()
    video_end_time = models.TimeField()
    created_on = models.DateTimeField(auto_now_add=True) 
    # video_call_url = models.URLField(blank=True, null=True)
    # is_enabled = models.BooleanField(default=False)

    # def enable_video_call(self):
    #     self.is_enabled = True
    #     self.video_call_url = generate_video_call_url(self.appointment.patient, self.appointment.doctor)
    #     self.save()

    def __str__(self):
        return f"Video Call for Appointment {self.appointment.id}"
