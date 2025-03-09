from rest_framework import serializers
from api.models import Student, User
from api.serializers.session_serializers import CourseSessionListSerializer
# from .user_serializers import UserSerializer

class StudentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    class Meta:
        model = Student
        fields = ["id", "user", "name", "birthdate"]

class StudentListSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    sessions = CourseSessionListSerializer(many=True, read_only=True)  # ✅ Now only includes courseName
    class Meta:
        model = Student
        fields = ["id", "user", "name", "birthdate", "sessions"]

    # def to_representation(self, instance):
    #     # When sending the response, include full user details
    #     representation = super().to_representation(instance)
    #     representation['user'] = UserSerializer(instance.user).data  # Full user details in response
    #     return representation