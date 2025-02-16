from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from api.permissions import IsAdmin
from api.models import CourseSession
from api.serializers import CourseSessionSerializer, AttendanceSerializer
from datetime import timedelta

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