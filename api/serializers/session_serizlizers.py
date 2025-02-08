from rest_framework import serializers
from api.models import CourseSession
from .course_serializers import CourseSerializer
from .teacher_serializers import TeacherSerializer
from .student_serializers import StudentSerializer


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