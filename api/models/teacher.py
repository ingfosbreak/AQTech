from django.db import models
from .user import User
from .category import Category

class Teacher(models.Model):
    STATUS_CHOICES = [
        ('active', 'active'),
        ('inactive', 'inactive'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="teachers")
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="teachers")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    def __str__(self):
        return self.name
     