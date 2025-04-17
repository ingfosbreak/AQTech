from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.models import Receipt, Student, CourseSession, User, Attendance
from django.shortcuts import get_object_or_404

class ReceiptDetails(APIView):
    def get(self, request, receipt_id):
        receipt = get_object_or_404(Receipt, id=receipt_id)
        student = receipt.student
        session = receipt.session
        course = session.course

        # Get attendances for this session
        attendances = Attendance.objects.filter(session=session).select_related("timeslot")

        attendance_list = []
        for att in attendances:
            attendance_list.append({
                "id": att.id,
                "status": att.status,
                "type": att.type,
                "date": att.attendance_date.isoformat(),
                "start_time": att.start_time.strftime("%H:%M") if att.start_time else None,
                "end_time": att.end_time.strftime("%H:%M") if att.end_time else None,
                "timeslot_id": att.timeslot.id if att.timeslot else None
            })

        response_data = {
            "id": receipt.id,
            "receipt_number": receipt.receipt_number,
            "student": {
                "name": student.name,
                "email": student.user.email,
                "id": f"STU-{str(student.id).zfill(3)}",
                "phone": student.user.contact or "N/A",
            },
            "session": {
                "course_name": course.name,
                "course_id": course.id,
                "category": course.category.categoryName,
                "total_quota": session.total_quota,
            },
            "attendances": attendance_list,
            "amount": str(receipt.amount),
            "payment_date": receipt.payment_date.isoformat(),
            "payment_method": receipt.payment_method,
            "created_by": "System",  # Optional
            "notes": receipt.notes or "",
            "items": receipt.items or [],
        }

        return Response(response_data, status=status.HTTP_200_OK)

class ReceiptListView(APIView):
    def get(self, request):
        receipts = Receipt.objects.select_related("student", "session", "session__course").order_by("-payment_date")

        data = []
        for r in receipts:
            data.append({
                "id": r.id,
                "student_id": r.student.id,
                "student": r.student.name,
                "course_id": r.session.course.id,
                "course_name": r.session.course.name,  # ✅ ใช้ course name แทน session
                "session_id": r.session.id,
                "amount": float(r.amount),
                "payment_date": r.payment_date.isoformat(),
                "payment_method": r.payment_method,
                "receipt_number": r.receipt_number,
                "notes": r.notes,
                "items": r.items,
            })

        return Response(data, status=status.HTTP_200_OK)
    
class MyInvoiceView(APIView):
    def get(self, request):
        try:
            # Get all students related to the current user (assuming the user could have multiple students)
            students = Student.objects.filter(user=request.user)
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

        # ✅ Get all receipts for this student
        receipts = Receipt.objects.filter(student__in=students).select_related("session__course").order_by("-payment_date")

        all_data = []

        for receipt in receipts:
            session = receipt.session
            course = session.course

            # ✅ Get attendances for this session
            attendances = Attendance.objects.filter(session=session).select_related("timeslot")
            attendance_list = []
            for att in attendances:
                attendance_list.append({
                    "id": att.id,
                    "status": att.status,
                    "type": att.type,
                    "date": att.attendance_date.isoformat(),
                    "start_time": att.start_time.strftime("%H:%M") if att.start_time else None,
                    "end_time": att.end_time.strftime("%H:%M") if att.end_time else None,
                    "timeslot_id": att.timeslot.id if att.timeslot else None
                })

            # ✅ Push full receipt data
            all_data.append({
                "id": receipt.id,
                "receipt_number": receipt.receipt_number,
                "student": {
                    "id": f"STU-{str(receipt.student.id).zfill(3)}",
                    "name": receipt.student.name,
                    "email": receipt.student.user.email,
                    "phone": receipt.student.user.contact or "N/A",
                },
                "session": {
                    "course_name": course.name,
                    "course_id": course.id,
                    "category": course.category.categoryName,
                    "total_quota": session.total_quota,
                },
                "attendances": attendance_list,
                "amount": str(receipt.amount),
                "payment_date": receipt.payment_date.isoformat(),
                "payment_method": receipt.payment_method,
                "created_by": "System",
                "notes": receipt.notes or "",
                "items": receipt.items or [],
            })

        return Response(all_data, status=status.HTTP_200_OK)

class MyInvoiceDetailView(APIView):
    def get(self, request, receipt_id):

        # ✅ Get receipt if it belongs to the logged-in student
        receipt = get_object_or_404(Receipt.objects.select_related("session__course", "student__user"), id=receipt_id)

        session = receipt.session
        course = session.course

        # ✅ Attendance records for this session
        attendances = Attendance.objects.filter(session=session).select_related("timeslot")
        attendance_list = []
        for att in attendances:
            attendance_list.append({
                "id": att.id,
                "status": att.status,
                "type": att.type,
                "date": att.attendance_date.isoformat(),
                "start_time": att.start_time.strftime("%H:%M") if att.start_time else None,
                "end_time": att.end_time.strftime("%H:%M") if att.end_time else None,
                "timeslot_id": att.timeslot.id if att.timeslot else None
            })

        # ✅ Response format
        return Response({
            "receipt": {
                "id": receipt.id,
                "receipt_number": receipt.receipt_number,
                "amount": str(receipt.amount),
                "payment_date": receipt.payment_date.isoformat(),
                "payment_method": receipt.payment_method,
                "notes": receipt.notes or "",
                "items": receipt.items or [],
            },
            "student": {
                "id": f"STU-{str(receipt.student.id).zfill(3)}",
                "name": receipt.student.name,
                "email": receipt.student.user.email,
                "phone": receipt.student.user.contact or "N/A",
            },
            "course": {
                "id": course.id,
                "name": course.name,
                "category": course.category.categoryName,
                "total_quota": session.total_quota,
                "session_id": session.id,
            },
            "attendances": attendance_list
        }, status=status.HTTP_200_OK)
