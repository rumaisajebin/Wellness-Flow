# Generated by Django 5.0.7 on 2024-08-21 07:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appoinment', '0007_doctorschedule_min_consulting_time_booking'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='doctorschedule',
            name='min_consulting_time',
        ),
    ]
