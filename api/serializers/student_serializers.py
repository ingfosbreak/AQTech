from rest_framework import serializers
from api.models import Student, User, Course
from .course_serializers import CourseSerializer
# from .user_serializers import UserSerializer

class StudentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    courses = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), many=True  # 🔹 Allow updating courses
    )
    class Meta:
        model = Student
        fields = ["id", "user", "name", "birthdate", "courses"]

    # def to_representation(self, instance):
    #     # When sending the response, include full user details
    #     representation = super().to_representation(instance)
    #     representation['user'] = UserSerializer(instance.user).data  # Full user details in response
    #     return representation