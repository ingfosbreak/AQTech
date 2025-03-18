from rest_framework import serializers
from api.models import Course, Type

class CourseSerializer(serializers.ModelSerializer):
    type = serializers.PrimaryKeyRelatedField(queryset=Type.objects.all())  # Accepts typeId

    class Meta:
        model = Course
        fields = ["id", "courseName", "description", "type", "quota", "created_at"]
