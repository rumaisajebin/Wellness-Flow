from django.db import models
from account.models import CustomUser
from django.core.exceptions import ValidationError

class TimeSlot(models.Model):
    time = models.TimeField()

class Slot(models.Model):
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    time = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    is_booked = models.BooleanField(default=False)
    
    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError("End date cannot be earlier than start date.")
        
        if not self.time:
            raise ValidationError("A valid time slot must be selected.")

        # Optionally, check for overlapping slots
        overlapping_slots = Slot.objects.filter(
            doctor=self.doctor,
            start_date__lte=self.end_date,
            end_date__gte=self.start_date,
            time=self.time
        ).exclude(id=self.id)
        
        if overlapping_slots.exists():
            raise ValidationError("This time slot overlaps with an existing slot.")
        
        super().clean()

class Booking(models.Model):
    slot = models.OneToOneField(Slot, on_delete=models.CASCADE)
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False)
