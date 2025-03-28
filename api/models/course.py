from django.db import models
from .category import Category

class Course(models.Model):
    TYPE_CHOICES = [
        ('restricted', 'restricted'),
        ('unrestricted', 'unrestricted'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='unrestricted')
    min_age = models.IntegerField(null=True)
    max_age = models.IntegerField(null=True)
    quota = models.IntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    price = models.IntegerField(default=3500)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="courses")
    def __str__(self):
        return self.name
 
