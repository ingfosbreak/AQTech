from django.db import models
from .session import CourseSession
from .student import Student
from .teacher import Teacher
from .timeslot import Timeslot

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'present'),
        ('absent', 'absent'),
    ]

    TYPE_CHOICES = [
        ('scheduled', 'scheduled'),
        ('makeup', 'makeup'),
    ]

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='absent')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='scheduled')
    session = models.ForeignKey(CourseSession, on_delete=models.CASCADE, related_name="attendances")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendances")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="attendances")
    timeslot = models.ForeignKey(Timeslot, on_delete=models.CASCADE, related_name="attendances")
    attendance_date = models.DateField()
    start_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)
    checked_date = models.DateTimeField(null=True, blank=True)
