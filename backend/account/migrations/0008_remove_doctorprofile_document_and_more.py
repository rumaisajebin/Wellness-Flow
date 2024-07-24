# Generated by Django 5.0.6 on 2024-07-23 04:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0007_doctorprofile_is_block'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='doctorprofile',
            name='document',
        ),
        migrations.AddField(
            model_name='doctorprofile',
            name='certificates_degrees',
            field=models.FileField(blank=True, null=True, upload_to='documents/certificates_degrees/'),
        ),
        migrations.AddField(
            model_name='doctorprofile',
            name='curriculum_vitae',
            field=models.FileField(blank=True, null=True, upload_to='documents/cv/'),
        ),
        migrations.AddField(
            model_name='doctorprofile',
            name='identification_document',
            field=models.FileField(blank=True, null=True, upload_to='documents/identification_documents/'),
        ),
        migrations.AddField(
            model_name='doctorprofile',
            name='medical_license_certificate',
            field=models.FileField(blank=True, null=True, upload_to='documents/medical_license_certificates/'),
        ),
        migrations.AddField(
            model_name='doctorprofile',
            name='proof_of_work',
            field=models.FileField(blank=True, null=True, upload_to='documents/proof_of_work/'),
        ),
        migrations.AddField(
            model_name='doctorprofile',
            name='specialization_certificates',
            field=models.FileField(blank=True, null=True, upload_to='documents/specialization_certificates/'),
        ),
    ]
