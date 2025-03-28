from django.db import models
from .course import Course
from .teacher import Teacher

class TeacherAssignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="assigns")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="assigns")
    
    ## edit เพิ่มอาจารย์ได้ทีหลัง 