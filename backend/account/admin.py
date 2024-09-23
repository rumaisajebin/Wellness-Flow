from django.contrib import admin
from .models import DoctorProfile,PatientProfile,CustomUser,AdminProfile,Notification
# Register your models here.

admin.site.register(CustomUser)
admin.site.register(PatientProfile)
admin.site.register(DoctorProfile)
admin.site.register(AdminProfile)
admin.site.register(Notification)