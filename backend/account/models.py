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
    is_verify = models.BooleanField(default=False)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    
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
    
    VERIFICATION_STATUS_CHOICES = [
    ('pending', 'Pending Review'),
    ('in_progress', 'In Progress'),
    ('approved', 'Approved'),
    ('denied', 'Denied'),
]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='doctor_profile')
    full_name = models.CharField(max_length=100)
    phone_number = models.IntegerField(null=True)
    address = models.TextField(null=True)
    bio = models.TextField(null=True)
    medical_license_no = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    graduation_year = models.IntegerField(null=True)
    years_of_experience = models.IntegerField(null=True)
    workplace_name = models.CharField(max_length=100)
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=200.00)
    profile_pic = models.ImageField(upload_to='profile/', null=True)
    medical_license_certificate = models.FileField(upload_to='documents/medical_license_certificates/', null=True)
    identification_document = models.FileField(upload_to='documents/identification_documents/', null=True)
    certificates_degrees = models.FileField(upload_to='documents/certificates_degrees/', null=True)
    curriculum_vitae = models.FileField(upload_to='documents/cv/', null=True)
    proof_of_work = models.FileField(upload_to='documents/proof_of_work/', null=True)
    specialization_certificates = models.FileField(upload_to='documents/specialization_certificates/', null=True)
    rejection_reason = models.TextField(null=True, blank=True)
    is_profile_verify = models.CharField(max_length=50, choices=VERIFICATION_STATUS_CHOICES, default='pending')
    

    def is_complete(self):
        required_fields = [
            self.profile_pic,
            self.full_name,
            self.phone_number,
            self.address,
            self.bio,
            self.medical_license_no,
            self.specialization,
            self.graduation_year,
            self.years_of_experience,
            self.workplace_name,
            self.medical_license_certificate,
            self.identification_document,
            self.certificates_degrees,
            self.curriculum_vitae,
            self.proof_of_work,
            self.specialization_certificates,
        ]
        return all(required_fields)
    
    def __str__(self):
        return self.user.username
    
class PatientProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='patient_profile')
    profile_pic = models.ImageField(upload_to='profile/patient',null = True)
    full_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True)
    age = models.IntegerField(null = True)
    phone_number = models.IntegerField(null = True)
    gender = models.CharField(max_length=10)
    address = models.TextField(null = True)

    def is_complete(self):
        required_fields = [
            self.profile_pic,
            self.full_name,
            self.date_of_birth,
            self.age,
            self.phone_number,
            self.gender,
            self.address,
            ]
        return all(required_fields)
    
    def __str__(self):
        return self.user.username
    
    
class AdminProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=3.00)  

    def __str__(self):
        return self.user.username
    

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message
