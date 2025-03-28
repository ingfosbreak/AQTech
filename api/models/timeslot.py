from django.db import models
from .course import Course


class Timeslot(models.Model): 
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="timeslots")
    timeslot_date = models.DateField()
    start_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)
 