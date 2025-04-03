from collections import defaultdict
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from api.models.attendance import Attendance
from api.models.student import Student
from api.permissions import IsAdmin
from api.models import CourseSession
from api.serializers import CourseSessionSerializer, AttendanceSerializer
from datetime import timedelta
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count

class SessionView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdmin]

    def post(self, request):
        # Validate CourseSession data
        course_session_serializer = CourseSessionSerializer(data=request.data)

        if not course_session_serializer.is_valid():
            return Response(course_session_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        course_session = course_session_serializer.save()
        
        # Prepare Attendance data
        teacher = course_session.teacher
        student = course_session.student
        session_date = course_session.session_date

        attendance_data = [
            {
                "session": course_session.id,  # Now we can use the saved session ID
                "teacher": teacher.id,
                "student": student.id,
                "attendance_date": session_date + timedelta(days=i * 7),
                "status": "absent"  # Set to "absent" by default
            }
            for i in range(10)
        ]

        attendance_serializer = AttendanceSerializer(data=attendance_data, many=True)

        if not attendance_serializer.is_valid():
            return Response(attendance_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Save Attendance records
        attendance_serializer.save()

        return Response({"message": "Created CourseSession Success"}, status=status.HTTP_201_CREATED)
    
class SessionProgressView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

        student_id = request.GET.get("studentId")
        if not student_id:
            return Response({"error": "studentId is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure the student exists and belongs to the logged-in user
        student = get_object_or_404(Student, id=student_id, user=request.user)

        # Fetch all course sessions for the student
        sessions = CourseSession.objects.filter(student=student)

        # Prepare session progress data
        session_data = []
        for session in sessions:
            total_classes = session.total_quota  # Uses related_name
            attended_classes = session.attendances.filter(status="present").count()

            session_data.append({
                "id": session.id,
                "title": session.course.courseName,
                "description": session.course.description,
                "totalClasses": total_classes,
                "attendedClasses": attended_classes,
                "startDate": session.session_date,
                "endDate": session.session_date + timedelta(weeks=10),
            })

        return Response(session_data, status=status.HTTP_200_OK)

class SessionProgressDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

        student_id = request.GET.get("studentId")
        session_id = request.GET.get("sessionId")

        if not student_id or not session_id:
            return Response({"error": "studentId and sessionId are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure the student exists and belongs to the logged-in user
        student = get_object_or_404(Student, id=student_id, user=request.user)

        # Get the specific session
        session = get_object_or_404(CourseSession, id=session_id, student=student)

        # Fetch all attendance records for this session and student
        attendance_records = Attendance.objects.filter(session=session, student=student).order_by("attendance_date")

        # Format attendance data
        attendance_data = [
            {
                "attendanceDate": record.attendance_date,
                "status": record.status,
                "checkedDate": record.checked_date,
            }
            for record in attendance_records
        ]

        # Prepare session details
        session_data = {
            "id": session.id,
            "title": session.course.courseName,
            "description": session.course.description,
            "totalClasses": session.total_quota,
            "attendedClasses": session.attendances.filter(student=student, status="present").count(),
            "startDate": session.session_date,
            "endDate": session.session_date + timedelta(weeks=10),
            "attendanceRecords": attendance_data,  # ✅ List of all attendance records
        }

        return Response(session_data, status=status.HTTP_200_OK)
    
class CourseCategoryEnrollmentView(APIView):
    def get(self, request):
        # Query to get enrollments per category
        course_enrollments = (
            CourseSession.objects
            .values('course__category__categoryName')  # Reference to Category's categoryName via ForeignKey
            .annotate(enrollments=Count('student'))  # Count the number of students per course
            .order_by('-enrollments')  # Order by enrollments
        )

        # Format data for frontend
        data = [
            {
                'category': enrollment['course__category__categoryName'],  # 'category' maps to categoryName
                'enrollments': enrollment['enrollments'],
            }
            for enrollment in course_enrollments
        ]
        
        return Response(data)