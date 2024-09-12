from django.db import models
from account.models import CustomUser
from appoinment.models import Booking
# Create your models here.

class Transaction(models.Model):
    STATUS_CHOICE = (
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed')
        
    )
    
    REFUND_STATUS_CHOICES = (
        ('not_refunded', 'Not Refunded'),
        ('refunded', 'Refunded'), 
    )
    
    
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='transactions', limit_choices_to={'role': 'patient'})
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='doctor_transactions', limit_choices_to={'role': 'doctor'})
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='transaction')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICE, default='pending')
    stripe_charge_id = models.CharField(max_length=255, blank=True, null=True)  # Stripe charge ID for tracking
    timestamp = models.DateTimeField(auto_now_add=True)
    refund_status = models.CharField(max_length=20, choices=REFUND_STATUS_CHOICES, default='not_refunded')
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"Transaction for Booking {self.booking.id} - {self.status}"
    