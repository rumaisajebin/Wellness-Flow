# Generated by Django 5.0.7 on 2024-08-22 06:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0019_rename_is_verify_doctorprofile_is_profile_verify'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctorprofile',
            name='fee',
            field=models.DecimalField(decimal_places=2, default=200.0, max_digits=10),
        ),
    ]