from rest_framework import serializers
from api.models import Teacher, User

class TeacherSerializer(serializers.ModelSerializer):
    # Add these fields to expose user details
    contact = serializers.CharField(source='user.contact', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    firstname = serializers.CharField(source='user.first_name', read_only=True)
    lastname = serializers.CharField(source='user.last_name', read_only=True)

    class Meta:
        model = Teacher
        fields = ["id", "user", "name", "contact", "username", "firstname", "lastname"]
