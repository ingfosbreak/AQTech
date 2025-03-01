from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from api.models import Student, Teacher, CourseSession

class CombinedCountView(APIView):
    def get(self, request):
        # Get counts for both students and teachers
        student_count = Student.objects.aggregate(count=Count('id'))['count']
        teacher_count = Teacher.objects.aggregate(count=Count('id'))['count']
        session_count = CourseSession.objects.aggregate(count=Count('id'))['count']
        
        
        # Return both counts in the response
        return Response(
            {"student_count": student_count, "teacher_count": teacher_count, "session_count": session_count, "session_count2": session_count+1},
            status=status.HTTP_200_OK
        )

class PieChartStaticView(APIView):
    def get(self, request):
        student_count = Student.objects.aggregate(count=Count('id'))['count']
        teacher_count = Teacher.objects.aggregate(count=Count('id'))['count']

        data = [
            {"name": "Student", "value": student_count},
            {"name": "Teacher", "value": teacher_count}
        ]

        return Response(data, status=status.HTTP_200_OK)

