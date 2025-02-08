from django.db import models
from .user import User

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="teacher")
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
