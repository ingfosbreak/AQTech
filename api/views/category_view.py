# views.py
from rest_framework import generics
from api.models import Category
from api.serializers import CategorySerializer

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()  # Query to get all categories
    serializer_class = CategorySerializer  # Specify the serializer to use

class CategoryCreateView(generics.CreateAPIView):
    queryset = Category.objects.all()  # This will be used by the CreateAPIView
    serializer_class = CategorySerializer  # Specify the serializer to use