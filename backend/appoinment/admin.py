from django.contrib import admin
from .models import DoctorSchedule,Booking
# Register your models here.


admin.site.register(DoctorSchedule)
admin.site.register(Booking)
# admin.site.register(Slot)
# admin.site.register(TimeSlot)