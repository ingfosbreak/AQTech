from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('staff', 'Staff'),
        ('user', 'User'),
        ('teacher', 'Teacher')
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    contact = models.CharField(max_length=15, blank=True, null=True)  # New phone number field
