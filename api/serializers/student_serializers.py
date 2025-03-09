from rest_framework import serializers
from api.models import Student, User
from api.models.session import CourseSession
# from .user_serializers import UserSerializer

class StudentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    course_sessions = serializers.PrimaryKeyRelatedField(
        many=True, queryset=CourseSession.objects.all()
    )
    class Meta:
        model = Student
        fields = ["id", "user", "name", "birthdate", "course_sessions"]


    # def to_representation(self, instance):
    #     # When sending the response, include full user details
    #     representation = super().to_representation(instance)
    #     representation['user'] = UserSerializer(instance.user).data  # Full user details in response
    #     return representation