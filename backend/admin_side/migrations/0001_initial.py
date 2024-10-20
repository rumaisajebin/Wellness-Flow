# Generated by Django 5.0.7 on 2024-10-18 13:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Agreement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('agreement_terms', models.TextField(default="**Agreement Terms**\n\n**1. Purpose:**\nThis Agreement outlines the terms and conditions under which the Admin will receive a commission from the Doctor’s fees for medical services provided.\n\n**2. Commission Rate:**\nThe Admin will receive a commission of 3% on the Doctor’s total fees collected from patients.\n\n**3. Fee Documentation:**\nThe Doctor agrees to document and report all fees charged for their services in a timely manner. The commission will be calculated based on the fees reported and verified by the Admin.\n\n**4. Payment Terms:**\n- The Admin’s commission will be calculated on a monthly basis and paid within 15 days of the end of each month.\n- Payment will be made via bank transfer or any other mutually agreed payment method.\n\n**5. Duration:**\nThis Agreement is effective from the date of signing and will remain in force until terminated by either party.\n\n**6. Termination:**\nEither party may terminate this Agreement with 30 days’ written notice. In the event of termination, any outstanding commissions will be paid according to the terms of this Agreement.\n\n**7. Confidentiality:**\nBoth parties agree to maintain the confidentiality of all financial and personal information related to this Agreement.\n\n**8. Dispute Resolution:**\nAny disputes arising from this Agreement will be resolved through arbitration in accordance with local laws.\n\n**9. Governing Law:**\nThis Agreement will be governed by and construed in accordance with the laws of [Your Country/State].\n\n**10. Amendments:**\nAny amendments to this Agreement must be made in writing and signed by both parties.\n\n**Signed:**\n\n_________________________  \n**Doctor**  \nName: [Doctor's Name]  \nDate: [Date]\n\n_________________________  \n**Admin**  \nName: [Admin's Name]  \nDate: [Date]\n")),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('terminated', 'Terminated')], max_length=20)),
                ('privacy_accepted', models.BooleanField(default=False)),
                ('signed', models.BooleanField(default=False)),
                ('admin', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='account.adminprofile')),
                ('doctor', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='account.doctorprofile')),
            ],
        ),
    ]
