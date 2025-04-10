from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.models import Receipt, Student, CourseSession, User
from django.shortcuts import get_object_or_404

class ReceiptDetails(APIView):
    def get(self, request, receipt_id):
        # Fetch the receipt by ID
        receipt = get_object_or_404(Receipt, id=receipt_id)
        
        # Fetch related data
        student = receipt.student
        session = receipt.session
        
        # Format receipt number (assuming it's numeric)
        receipt_number = receipt.receipt_number
        
        # Get session details (like instructor, schedule, location)
        session_details = {
            "name": session.name,
            "course_name": session.course.name,  # Assuming teacher is assigned
            "category": session.course.category.categoryName,
            "total_quota": session.total_quota,  # Placeholder
        }

        # Prepare the items (assuming JSON format already)
        items = receipt.items if receipt.items else []

        # Prepare the response data
        response_data = {
            "id": receipt.id,
            "receipt_number": receipt_number,
            "student": {
                "name": student.name,
                "email": student.user.email,
                "id": f"STU-{str(student.id).zfill(3)}",  # Assuming you want to format student ID as "STU-001"
                "phone": student.user.contact or "N/A",  # If phone exists
            },
            "session": session_details,
            "amount": str(receipt.amount),  # Assuming you want to return the amount as a string
            "payment_date": receipt.payment_date.isoformat(),
            "payment_method": receipt.payment_method,
            "created_by": "System",  # You can adjust this as needed (e.g., use `user` or request.user)
            "notes": receipt.notes or "",
            "items": items,
        }

        # Return the formatted data in the response
        return Response(response_data, status=status.HTTP_200_OK)

class ReceiptListView(APIView):
    def get(self, request):
        receipts = Receipt.objects.all().order_by("-payment_date")

        data = []
        for r in receipts:
            data.append({
                "id": r.id,
                "student": r.student.name,
                "session": r.session.name,
                "amount": float(r.amount),
                "payment_date": r.payment_date.isoformat(),
                "payment_method": r.payment_method,
                "receipt_number": r.receipt_number,
            })

        return Response(data, status=status.HTTP_200_OK)
