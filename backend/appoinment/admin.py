from django.contrib import admin
from .models import Booking,Slot,TimeSlot
# Register your models here.
admin.site.register(Booking)
admin.site.register(Slot)
admin.site.register(TimeSlot)