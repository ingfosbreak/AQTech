from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from api.permissions import IsAdmin
from api.models import Attendance, CourseSession, Student
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from django.forms.models import model_to_dict
from django.db.models import Prefetch
import urllib.parse

class AttendanceView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdmin]

    def post(self, request):
        session_id = request.data.get("session_id")
        date_str = request.data.get("date")
        start_time_str = request.data.get('start_time')
        
        if not session_id:
            return JsonResponse({"error": "Missing required parameters."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            session = CourseSession.objects.get(id=session_id)
        except (CourseSession.DoesNotExist):
            return JsonResponse({"error": "session not found."}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            decoded_date_str = urllib.parse.unquote(date_str)
            date_obj = timezone.datetime.strptime(decoded_date_str, "%Y-%m-%dT%H:%M:%S.%fZ").date()
            start_time = datetime.strptime(start_time_str, "%I:%M %p").time()  # Parse start time
        except ValueError as e:
            return JsonResponse({"error": e}, status=status.HTTP_400_BAD_REQUEST)
        
        today = timezone.localtime().date()
        now = timezone.localtime()
        start_datetime = datetime.combine(date_obj, start_time)
        start_datetime = timezone.make_aware(start_datetime, timezone.get_current_timezone())
        end_datetime = start_datetime + timedelta(hours=1)
        end_time = end_datetime.time()

        if date_obj < today:
            return JsonResponse({"error": "The date must be today or in the future."}, status=status.HTTP_400_BAD_REQUEST)
        
        if date_obj == today:
            if start_datetime <= now:
                return JsonResponse({"error": "The start time must be in the future."}, status=status.HTTP_400_BAD_REQUEST)

        existing_attendance = Attendance.objects.filter(
            session=session,
            attendance_date=date_obj,
            start_time=start_time
        ).first()

        if existing_attendance:
            return JsonResponse({"error": "Attendance for today has already been recorded."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create the attendance record
            attendance = Attendance.objects.create(
                status="absent",
                session=session,
                student=session.student,
                teacher=session.teacher,
                attendance_date=date_obj,
                start_time=start_time,
                end_time=end_time,
            )

        except Exception as e:
        # Log the exception and return an error
            print(f"Error creating attendance: {e}")  # Log error to console
            return JsonResponse({"error": e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return JsonResponse(model_to_dict(attendance), safe=False, status=status.HTTP_200_OK)


class AttendanceModifyView(APIView):

    def get(self, request):
        try:
            # Prefetch related sessions and attendances for each student
            attendances_prefetch = Prefetch('attendances', queryset=Attendance.objects.all(), to_attr='attendances_list')

            # Load students and prefetch their sessions and attendances
            students = Student.objects.prefetch_related(
                Prefetch('sessions', queryset=CourseSession.objects.all().prefetch_related(attendances_prefetch), to_attr='sessions_list')
            ).all()

            # Prepare response data
            result = []
            for student in students:
                student_data = model_to_dict(student)
                student_data['username'] = student.user.username
                student_data['sessions'] = []
                
                for session in student.sessions_list:
                    session_data = model_to_dict(session)
                    session_data['session_name'] = session.course.courseName
                    session_data['attendances'] = []

                    # Map attendance to each session
                    for attendance in session.attendances_list:
                        session_data['attendances'].append(model_to_dict(attendance))

                    student_data['sessions'].append(session_data)

                result.append(student_data)

            return Response(result, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": f"Something went wrong: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)