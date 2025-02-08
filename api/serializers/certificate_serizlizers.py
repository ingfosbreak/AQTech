from rest_framework import serializers
from api.models import Certificate
from .user_serializers import UserSerializer
from .course_serializers import CourseSerializer

class CertificateSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    course = CourseSerializer()

    class Meta:
        model = Certificate
        fields = ["id", "user", "course", "status"]
