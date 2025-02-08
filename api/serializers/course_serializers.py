from rest_framework import serializers
from api.models import Course
from .level_serializers import LevelSerializer

class CourseSerializer(serializers.ModelSerializer):
    level = LevelSerializer()

    class Meta:
        model = Course
        fields = ["id", "courseName", "description", "level"]