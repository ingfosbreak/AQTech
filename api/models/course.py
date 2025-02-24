from django.db import models
from .level import Level

class Course(models.Model):
    courseName = models.CharField(max_length=100)
    description = models.TextField()
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name="courses")
    #quota_number

    def __str__(self):
        return self.courseName

# how many qouta field