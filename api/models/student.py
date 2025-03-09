from django.db import models
from .course import Course
from .user import User
from datetime import date

class Student(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="students")
    name = models.CharField(max_length=100)
    birthdate = models.DateField(default=date.today)
    course_sessions = models.ManyToManyField("CourseSession", related_name="students")
    # picture

    def __str__(self):
        return self.name
