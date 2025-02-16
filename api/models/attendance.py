from django.db import models
from .session import CourseSession
from .student import Student
from .teacher import Teacher

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
    ]

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='absent')
    session = models.ForeignKey(CourseSession, on_delete=models.CASCADE, related_name="attendances")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendances")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="attendances")
    attendance_date = models.DateField()
    checked_date = models.DateTimeField(null=True, blank=True)
    # comment = models.TextField(null=True, blank=True)  # Added comment field
