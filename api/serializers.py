from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import (
    Student, Teacher, Level, Course, CourseSession,
    Attendance, Certificate, Receipt, Storage
)

User = get_user_model()

# 🔹 User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "role"]

# 🔹 Student Serializer
class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Includes user details

    class Meta:
        model = Student
        fields = ["id", "user", "name", "dob", "contact", "email"]

# 🔹 Teacher Serializer
class TeacherSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Teacher
        fields = ["id", "user", "name"]

# 🔹 Level Serializer
class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ["id", "levelName"]

# 🔹 Course Serializer
class CourseSerializer(serializers.ModelSerializer):
    level = LevelSerializer()

    class Meta:
        model = Course
        fields = ["id", "courseName", "description", "level"]

# 🔹 Course Session Serializer
class CourseSessionSerializer(serializers.ModelSerializer):
    course = CourseSerializer()
    teacher = TeacherSerializer()
    student = StudentSerializer()

    class Meta:
        model = CourseSession
        fields = [
            "id", "course", "teacher", "student",
            "session_number", "session_date", "total_quota",
            "start_time", "end_time"
        ]

# 🔹 Attendance Serializer
class AttendanceSerializer(serializers.ModelSerializer):
    session = CourseSessionSerializer()
    student = StudentSerializer()
    teacher = TeacherSerializer()

    class Meta:
        model = Attendance
        fields = ["id", "session", "student", "teacher", "status", "checked_date"]

# 🔹 Certificate Serializer
class CertificateSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    course = CourseSerializer()

    class Meta:
        model = Certificate
        fields = ["id", "user", "course", "status"]

# 🔹 Receipt Serializer
class ReceiptSerializer(serializers.ModelSerializer):
    student = StudentSerializer()
    session = CourseSessionSerializer()

    class Meta:
        model = Receipt
        fields = [
            "id", "student", "session", "amount",
            "payment_date", "payment_method", "transaction_id"
        ]

# 🔹 Storage Serializer
class StorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Storage
        fields = ["id", "title", "storage_image", "quantiry"]
