from rest_framework import serializers
from api.models import Course, Level

class CourseSerializer(serializers.ModelSerializer):
    level = serializers.PrimaryKeyRelatedField(queryset=Level.objects.all())  # Accepts levelId

    class Meta:
        model = Course
        fields = ["id", "courseName", "description", "level", "quota", "created_at"]
