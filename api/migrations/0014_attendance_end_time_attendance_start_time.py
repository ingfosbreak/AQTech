# Generated by Django 5.1.5 on 2025-03-18 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_remove_student_contact_remove_student_dob_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='end_time',
            field=models.TimeField(null=True),
        ),
        migrations.AddField(
            model_name='attendance',
            name='start_time',
            field=models.TimeField(null=True),
        ),
    ]
