# Generated by Django 5.0.6 on 2024-07-08 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_alter_patientprofile_date_of_birth'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctorprofile',
            name='phone_number',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='patientprofile',
            name='phone_number',
            field=models.IntegerField(null=True),
        ),
    ]
