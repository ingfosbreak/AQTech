from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from api.permissions import IsAdmin
from api.models import Attendance, CourseSession
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta

class AttendanceView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdmin]

    def post(self, request):
        session_id = request.data.get("session_id")
        date_str = request.data.get("date")
        
        if not session_id:
            return JsonResponse({"error": "Missing required parameters."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            session = CourseSession.objects.get(id=session_id)
        except (CourseSession.DoesNotExist):
            return JsonResponse({"error": "session not found."}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            date_obj = timezone.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ").date()
        except ValueError:
            return JsonResponse({"error": "Invalid date format."}, status=status.HTTP_400_BAD_REQUEST)
        
        today = timezone.now().date()
        if date_obj < today:
            return JsonResponse({"error": "The date must be today or in the future."}, status=status.HTTP_400_BAD_REQUEST)
        
        existing_attendance = Attendance.objects.filter(
            session=session,
            attendance_date=date_obj
        ).first()

        if existing_attendance:
            return JsonResponse({"error": "Attendance for today has already been recorded."}, status=status.HTTP_400_BAD_REQUEST)

        attendance = Attendance.objects.create(
            status="absent",
            session=session,
            student=session.student,
            teacher=session.teacher,
            attendance_date=date_obj
        )

        return JsonResponse(attendance, safe=False, status=status.HTTP_200_OK)