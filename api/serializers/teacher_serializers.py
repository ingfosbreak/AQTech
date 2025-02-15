from rest_framework import serializers
from api.models import Teacher, User
# from .user_serializers import UserSerializer

class TeacherSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Teacher
        fields = ["id", "user", "name"]