from django.db import models
from .course import Course
from .teacher import Teacher
from .student import Student

class CourseSession(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sessions")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="sessions")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="sessions")

    session_number = models.IntegerField()
    session_date = models.DateField()
    total_quota = models.IntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    ## not sure