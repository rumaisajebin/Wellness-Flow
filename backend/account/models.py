from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.db.models.signals import post_save


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('doctor', 'Doctor'),
        ('patient','Patient'),
    ]
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=7,choices=ROLE_CHOICES )
    
    REQUIRED_FIELDS = ['email']
    
    def __str__(self) -> str:
        return self.username

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'doctor':
            DoctorProfile.objects.create(user=instance)
        else:
            PatientProfile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)     
def save_user_profile(sender, instance, **kwargs):
    if instance.role == 'doctor':
        instance.doctor_profile.save()
    elif instance.role == 'patient':
        instance.patient_profile.save()
        
class DoctorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='doctor_profile')
    full_name = models.CharField(max_length=100)
    phone_number = models.IntegerField(null = True)
    medical_license_no = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    graduation_year = models.IntegerField(null = True)
    years_of_experience = models.IntegerField(null = True)
    workplace_name = models.CharField(max_length=100)
    document = models.FileField(upload_to='documents/')
    is_verify = models.BooleanField(default = False)
    
    def __str__(self):
        return self.user.username
    
class PatientProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='patient_profile')
    full_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True)
    age = models.IntegerField(null = True)
    phone_number = models.IntegerField(null = True)
    gender = models.CharField(max_length=10)
    address = models.TextField()

    def __str__(self):
        return self.user.username