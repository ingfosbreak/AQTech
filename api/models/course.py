from django.db import models
from .type import Type

class Course(models.Model):
    courseName = models.CharField(max_length=100)
    description = models.TextField()
    type = models.ForeignKey(Type, on_delete=models.CASCADE, related_name="courses")
    quota = models.IntegerField(default=10)  # Added quota_number field
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.courseName

# how many qouta field