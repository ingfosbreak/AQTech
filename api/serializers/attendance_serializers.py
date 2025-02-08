from rest_framework import serializers
from api.models import Attendance
from .session_serizlizers import CourseSessionSerializer
from .teacher_serializers import TeacherSerializer
from .student_serializers import StudentSerializer


class AttendanceSerializer(serializers.ModelSerializer):
    session = CourseSessionSerializer()
    student = StudentSerializer()
    teacher = TeacherSerializer()

    class Meta:
        model = Attendance
        fields = ["id", "session", "student", "teacher", "status", "checked_date"]