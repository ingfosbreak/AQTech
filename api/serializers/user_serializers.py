from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

# 🔹 User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password", "email", "role", "first_name", "last_name"]