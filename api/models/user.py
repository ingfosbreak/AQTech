from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date

class User(AbstractUser):
    ROLE_CHOICES = (
        ('staff', 'Staff'),
        ('user', 'User'),
        ('teacher', 'Teacher')
    )
    join_date = models.DateField(default=date.today)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    contact = models.CharField(max_length=15, blank=True, null=True)  # New phone number field
