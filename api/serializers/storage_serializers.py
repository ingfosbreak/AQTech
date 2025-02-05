from rest_framework import serializers
from api.models import Storage

class StorageSerializer(serializers.ModelSerializer):
    storage_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Storage
        fields = ["id", "title", "storage_image", "quantity"]

    def validate_quantity(self, value):
        # Custom validation to ensure quantity isn't negative
        if value < 0:
            raise serializers.ValidationError('Quantity cannot be lower than 0.')
        return value