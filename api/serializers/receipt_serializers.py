from rest_framework import serializers
from api.models import Receipt
from .student_serializers import StudentSerializer
from .session_serializers import CourseSessionSerializer

class ReceiptSerializer(serializers.ModelSerializer):
    student = StudentSerializer()
    session = CourseSessionSerializer()

    class Meta:
        model = Receipt
        fields = [
            "id", "student", "session", "amount",
            "payment_date", "payment_method", "transaction_id"
        ]
