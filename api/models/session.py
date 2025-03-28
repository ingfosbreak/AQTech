from django.db import models
from .course import Course
from .teacher import Teacher
from .student import Student

class CourseSession(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sessions")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="sessions")
    name = models.CharField(max_length=100)
    total_quota = models.IntegerField() 

 