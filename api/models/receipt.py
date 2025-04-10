from django.db import models
from .student import Student
from .session import CourseSession

class Receipt(models.Model):

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="receipts")
    session = models.ForeignKey(CourseSession, on_delete=models.CASCADE, related_name="receipts")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    
    receipt_number = models.CharField(max_length=20, unique=True)  # Unique identifier for the receipt
    payment_method = models.CharField(max_length=50, choices=[
        ('CASH', 'Cash'),
        ('CARD', 'Credit/Debit Card'),
        ('TRANSFER', 'Bank Transfer'),
        ('CHECK', 'Check'),
        ('OTHER', 'Other')
    ])
    notes = models.TextField(blank=True, null=True)  # For any additional information
    # For itemized receipts (optional)
    items = models.JSONField(blank=True, null=True)  # Store line items as JSON
    
    # For tracking changes
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Receipt {self.receipt_number} - {self.student.name}"