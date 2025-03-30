from rest_framework import serializers
from api.models import Course, Category, TeacherAssignment
from api.models.session import CourseSession
from api.serializers.teacher_serializers import TeacherSerializer

class CourseSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())  # Accepts typeId

    class Meta:
        model = Course
        fields = ["id", "courseName", "description", "type", "quota", "created_at"]

class CoursePriceSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())  # Accepts typeId

    class Meta:
        model = Course
        fields = ["id", "courseName", "description", "type", "quota", "created_at", "price"]

class CourseDetailedSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.categoryName')
    enrolled = serializers.SerializerMethodField()
    teachers = serializers.SerializerMethodField()  # Custom method to fetch teachers

    class Meta:
        model = Course
        fields = [
            'id', 'name', 'description', 'type', 'min_age', 'max_age', 'quota', 'created_at', 'price', 'category', 'enrolled', 'teachers'
        ]

    def get_enrolled(self, obj):
        return CourseSession.objects.filter(course=obj).values('student').distinct().count()

    def get_teachers(self, obj):
        # Manually fetch teacher data
        teacher_assignments = TeacherAssignment.objects.filter(course=obj)
        return [{'id': assignment.teacher.id, 'name': assignment.teacher.name} for assignment in teacher_assignments]