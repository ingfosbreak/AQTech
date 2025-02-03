from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    ROLE_CHOICES = (
        ('staff', 'Staff'),
        ('user', 'User'),
        ('teacher', 'Teacher')
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

class Student(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="students")
    name = models.CharField(max_length=100)
    dob  = models.DateField()
    contact = models.CharField(max_length=15)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="teacher")
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Level(models.Model):
    levelName = models.CharField(max_length=50)

    def __str__(self):
        return self.levelName


class Course(models.Model):
    courseName = models.CharField(max_length=100)
    description = models.TextField()
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name="courses")

    def __str__(self):
        return self.courseName
    
class CourseSession(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sessions")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="sessions")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="sessions")

    session_number = models.IntegerField()
    session_date = models.DateField()
    total_quota = models.IntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    ## not sure

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
    ]

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='absent')
    session = models.ForeignKey(CourseSession, on_delete=models.CASCADE, related_name="attendances")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendances")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="attendances")
    checked_date = models.DateTimeField()
    ## comment field ??

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

class Storage(models.Model):
    title = models.CharField(max_length=100)
    storage_image = models.ImageField(upload_to="storages/", null=True, blank=True)
    quantiry = models.DecimalField(max_digits=10)