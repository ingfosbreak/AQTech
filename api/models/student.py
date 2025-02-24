from django.db import models
from .user import User

class Student(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="students")
    name = models.CharField(max_length=100)
    dob = models.DateField()
    contact = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    # picture

    def __str__(self):
        return self.name
