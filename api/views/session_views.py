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

            # Retrieve the first associated timeslot date (assuming there's at least one timeslot per session)
            timeslot = session.course.timeslots.first()  # Assuming there is one timeslot per session for simplicity
            if timeslot:
                start_date = timeslot.timeslot_date
                end_date = start_date + timedelta(weeks=10)
            else:
                start_date = None
                end_date = None

            session_data.append({
                "id": session.id,
                "title": session.course.name,
                "description": session.course.description,
                "totalClasses": total_classes,
                "attendedClasses": attended_classes,
                "startDate": start_date,
                "endDate": end_date,
            })

        return Response(session_data, status=status.HTTP_200_OK)

class SessionProgressDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

        # Get parameters from request
        student_id = request.GET.get("studentId")
        session_id = request.GET.get("sessionId")

        if not student_id or not session_id:
            return Response({"error": "studentId and sessionId are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate student and session
        student = get_object_or_404(Student, id=student_id, user=request.user)
        session = get_object_or_404(CourseSession, id=session_id, student=student)

        # Get related course and timeslots
        course = session.course
        timeslots = course.timeslots.all()

        # Fetch attendance records for these timeslots and student
        attendance_records = Attendance.objects.select_related(
            "student", "timeslot"
        ).filter(
            timeslot__in=timeslots,
            student=student
        ).order_by("attendance_date")

        # Calculate dates based on actual timeslots
        start_date = timeslots.first().timeslot_date if timeslots.exists() else None
        end_date = timeslots.last().timeslot_date if timeslots.exists() else None

        # Prepare attendance data
        attendance_data = []
        for record in attendance_records:
            attendance_data.append({
                "attendanceDate": record.attendance_date.strftime("%Y-%m-%d"),
                "status": record.status,
                "checkedDate": record.checked_date,
                "timeslotDate": record.timeslot.timeslot_date
            })

        # Build response
        session_data = {
            "id": session.id,
            "title": course.name,
            "description": course.description,
            "totalClasses": timeslots.count(),  # Using actual timeslot count
            "attendedClasses": attendance_records.filter(status="present").count(),
            "startDate": start_date,
            "endDate": end_date,
            "attendanceRecords": attendance_data,
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