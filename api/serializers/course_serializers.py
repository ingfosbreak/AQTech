from rest_framework import serializers
from api.models import Course, Category

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
