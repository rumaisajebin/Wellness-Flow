from django.db import models
from account.models import DoctorProfile,AdminProfile
from datetime import timedelta
# Create your models here.

class Agreement(models.Model):
    doctor = models.OneToOneField(DoctorProfile, on_delete=models.CASCADE)
    admin = models.OneToOneField(AdminProfile, on_delete=models.CASCADE)
    agreement_terms = models.TextField(default="""\
**Agreement Terms**

**1. Purpose:**
This Agreement outlines the terms and conditions under which the Admin will receive a commission from the Doctor’s fees for medical services provided.

**2. Commission Rate:**
The Admin will receive a commission of 3% on the Doctor’s total fees collected from patients.

**3. Fee Documentation:**
The Doctor agrees to document and report all fees charged for their services in a timely manner. The commission will be calculated based on the fees reported and verified by the Admin.

**4. Payment Terms:**
- The Admin’s commission will be calculated on a monthly basis and paid within 15 days of the end of each month.
- Payment will be made via bank transfer or any other mutually agreed payment method.

**5. Duration:**
This Agreement is effective from the date of signing and will remain in force until terminated by either party.

**6. Termination:**
Either party may terminate this Agreement with 30 days’ written notice. In the event of termination, any outstanding commissions will be paid according to the terms of this Agreement.

**7. Confidentiality:**
Both parties agree to maintain the confidentiality of all financial and personal information related to this Agreement.

**8. Dispute Resolution:**
Any disputes arising from this Agreement will be resolved through arbitration in accordance with local laws.

**9. Governing Law:**
This Agreement will be governed by and construed in accordance with the laws of [Your Country/State].

**10. Amendments:**
Any amendments to this Agreement must be made in writing and signed by both parties.

**Signed:**

_________________________  
**Doctor**  
Name: [Doctor's Name]  
Date: [Date]

_________________________  
**Admin**  
Name: [Admin's Name]  
Date: [Date]
""")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('terminated', 'Terminated')])
    privacy_accepted = models.BooleanField(default=False)
    signed = models.BooleanField(default=False)


    def save(self, *args, **kwargs):
        if not self.end_date:
            if self.start_date:
                self.end_date = self.start_date + timedelta(days=730)  # 730 days = 2 years
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Agreement between {self.doctor.user.username} and {self.admin.user.username}"