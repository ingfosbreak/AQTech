from rest_framework import serializers
from api.models import CourseSession
from api.models.attendance import Attendance
from .course_serializers import CourseSerializer
from .teacher_serializers import TeacherSerializer
# from .student_serializers import StudentSerializer
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

class CourseSessionListSerializer(serializers.ModelSerializer):
    courseName = serializers.CharField(source="course.courseName", read_only=True)  # ✅ Extracts only courseName

    class Meta:
        model = CourseSession
        fields = ["courseName"]  # ✅ Returns only courseName

class CourseProgressSerializer(serializers.ModelSerializer):
    totalClasses = serializers.SerializerMethodField()
    attendedClasses = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ["id", "title", "description", "totalClasses", "attendedClasses", "startDate", "endDate"]

    def get_totalClasses(self, obj):
        return obj.sessions.count()

    def get_attendedClasses(self, obj):
        child_id = self.context.get("child_id")
        if child_id:
            return Attendance.objects.filter(session__course=obj, student_id=child_id, attended=True).count()
        return 0