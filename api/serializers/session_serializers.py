from rest_framework import serializers
from api.models import CourseSession
from .course_serializers import CourseSerializer
from .teacher_serializers import TeacherSerializer
from .student_serializers import StudentSerializer
from api.models import Course, Teacher, Student


class CourseSessionSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())

    class Meta:
        model = CourseSession
        fields = [
            "id", "course", "teacher", "student", "session_date", "total_quota",
            "start_time", "end_time"
        ]