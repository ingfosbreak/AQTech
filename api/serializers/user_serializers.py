from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.hashers import make_password

from .student_serializers import StudentListSerializer, StudentSerializer

User = get_user_model()

# 🔹 User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password", "email", "role", "first_name", "last_name", "join_date" , "contact"]

    def validate_password(self, value: str) -> str:
        """
        Hash value passed by user.

        :param value: password of a user
        :return: a hashed version of the password
        """
        return make_password(value)

class UserListSerializer(serializers.ModelSerializer):
    students = StudentListSerializer(many=True, read_only=True)  # Include student details
    
    class Meta:
        model = User
        fields = ["id", "username", "password", "email", "role", "first_name", "last_name", "join_date" , "contact", "students"]

    def validate_password(self, value: str) -> str:
        """
        Hash value passed by user.

        :param value: password of a user
        :return: a hashed version of the password
        """
        return make_password(value)