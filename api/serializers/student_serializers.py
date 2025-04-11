from rest_framework import serializers
from api.models import Student, User
from api.serializers.session_serializers import CourseSessionListSerializer
# from .user_serializers import UserSerializer

class StudentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    class Meta:
        model = Student
        fields = ["id", "user", "name", "birthdate", "sessions", "status"]

class StudentListSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    sessions = CourseSessionListSerializer(many=True, read_only=True)
    
    # Add the status field from the Student model
    status = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Student
        fields = ["id", "user", "name", "birthdate", "sessions", "status"]

class StudentStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['status']  # Only allow the 'status' field to be updated

    # def to_representation(self, instance):
    #     # When sending the response, include full user details
    #     representation = super().to_representation(instance)
    #     representation['user'] = UserSerializer(instance.user).data  # Full user details in response
    #     return representation