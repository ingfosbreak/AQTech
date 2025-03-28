from rest_framework import serializers
from api.models import Category

class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "categoryName"]