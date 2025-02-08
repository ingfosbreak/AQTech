from django.db import models
from .user import User
from .course import Course

class Certificate(models.Model):
    STATUS_CHOICES = [
        ('issued', 'Issued'),
        ('revoked', 'Revoked'),
    ]

    ## ผูกกับประเภทคอร์ส
    ## มีรูปภาพ
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="certificates")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="certificates")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='issued')
    # issued_date = models.DateTimeField(auto_now_add=True)
    # certificate_image = models.ImageField(upload_to="certificates/", null=True, blank=True)