from django.db import models
from .student import Student
from .session import CourseSession

class Receipt(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('Cash', 'Cash'),
        ('Credit Card', 'Credit Card'),
        ('Bank Transfer', 'Bank Transfer'),
        ('E-Wallet', 'E-Wallet'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="receipts")
    session = models.ForeignKey(CourseSession, on_delete=models.CASCADE, related_name="receipts")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, unique=True) ##  what is this ??