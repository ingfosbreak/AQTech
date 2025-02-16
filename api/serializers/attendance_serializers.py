from rest_framework import serializers
from api.models import Attendance
from .session_serializers import CourseSessionSerializer
from .teacher_serializers import TeacherSerializer
from .student_serializers import StudentSerializer
from api.models import CourseSession, Teacher, Student


class AttendanceSerializer(serializers.ModelSerializer):
    session = serializers.PrimaryKeyRelatedField(queryset=CourseSession.objects.all())
    teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())

    class Meta:
        model = Attendance
        fields = ["id", "session", "student", "teacher", "status", "attendance_date", "checked_date"]