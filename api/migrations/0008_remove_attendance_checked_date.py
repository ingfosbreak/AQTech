# Generated by Django 5.1.5 on 2025-02-08 14:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_attendance_checked_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attendance',
            name='checked_date',
        ),
    ]
