# Generated by Django 5.0.7 on 2024-08-21 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appoinment', '0010_remove_booking_slot_end_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='schedule_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
