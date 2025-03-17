from rest_framework.generics import ListAPIView
from api.models import Course
from api.models.session import CourseSession
from api.models.student import Student
from api.serializers.course_serializers import CourseSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from api.models import Course, Level
from api.serializers.session_serializers import CourseSessionSerializer
from rest_framework.permissions import IsAuthenticated

class CourseListView(ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class CourseDetailView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdmin]

    def get(self, request, pk):
        try:
            storage = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CourseSerializer(storage)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class CourseCreateView(APIView):
    def post(self, request, *args, **kwargs):
        # Ensure `levelId` is present in the request data
        level_id = request.data.get("levelId")
        if not level_id:
            return Response({"error": "levelId is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            level = Level.objects.get(id=level_id)  # Fetch the Level by ID
        except Level.DoesNotExist:
            return Response({"error": "Invalid level ID"}, status=status.HTTP_400_BAD_REQUEST)

        # Attach level to the request data and validate the serializer
        request.data["level"] = level.id  # Attach the level ID to the data
        serializer = CourseSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CourseProgressAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        child_id = request.query_params.get("childId")

        if not child_id:
            return Response({"error": "childId is required"}, status=400)

        try:
            student = Student.objects.get(id=child_id, user=request.user)
        except Student.DoesNotExist:
            return Response({"error": "Student not found or unauthorized"}, status=404)

        sessions = CourseSession.objects.filter(student=student)
        serializer = CourseSessionSerializer(sessions, many=True)
        return Response(serializer.data)

class CompletedCoursesView(ListAPIView):
    serializer_class = CourseSessionSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        student_id = self.request.query_params.get("studentId")
        
        if not student_id:
            return CourseSession.objects.none()  # Return empty if no student ID
        
        # Filter sessions where total_quota is 0 (i.e., course is completed)
        return CourseSession.objects.filter(student_id=student_id, total_quota=0)
