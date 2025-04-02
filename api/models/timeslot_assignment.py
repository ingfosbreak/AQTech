from django.db import models
from .teacher import Teacher
from .timeslot import Timeslot

class TimeslotTeacherAssignment(models.Model):
    timeslot = models.ForeignKey(Timeslot, on_delete=models.CASCADE, related_name="timeslot_assignments")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="timeslot_assignments")

    def __str__(self):
        return f"{self.teacher.name} assigned to {self.timeslot}"