from rest_framework import serializers
from api.models import Teacher, Category, User

class TeacherSerializer(serializers.ModelSerializer):
    # Add user details to be included in the response
    contact = serializers.CharField(source='user.contact', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    firstname = serializers.CharField(source='user.first_name', read_only=True)
    lastname = serializers.CharField(source='user.last_name', read_only=True)

    # Use a SerializerMethodField for category name, and set the field name as 'category'
    category = serializers.SerializerMethodField()

    def get_category(self, obj):
        # Access and return the categoryName attribute of the related category object
        return obj.category.categoryName if obj.category else None

    class Meta:
        model = Teacher
        fields = [
            "id", 
            "user", 
            "status", 
            "name", 
            "contact", 
            "username", 
            "firstname", 
            "lastname", 
            "category",  # The field name will now be 'category' in the response
        ]