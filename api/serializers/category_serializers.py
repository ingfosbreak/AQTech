# serializers.py
from rest_framework import serializers
from api.models import Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'categoryName']  # You can include any fields you want to expose
