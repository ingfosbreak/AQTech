from django.db import models
from .student import Student
from .session import CourseSession

class Receipt(models.Model):

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="receipts")
    session = models.ForeignKey(CourseSession, on_delete=models.CASCADE, related_name="receipts")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    receipt_url = models.URLField(null=True, blank=True)