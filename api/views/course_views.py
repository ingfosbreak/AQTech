from rest_framework.generics import ListAPIView
from api.models import Course
from api.models.category import Category
from api.models.session import CourseSession
from api.models.student import Student
from api.serializers.course_serializers import CourseSerializer, CoursePriceSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from api.models import Course
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
    
class CoursePriceListView(ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CoursePriceSerializer

class CourseCreateView(APIView):
    def post(self, request, *args, **kwargs):
        # Ensure `categoryId` is present in the request data
        category_id = request.data.get("categoryId")
        if not category_id:
            return Response({"error": "categoryId is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            category = Category.objects.get(id=category_id)  # Fetch the category by ID
        except category.DoesNotExist:
            return Response({"error": "Invalid category ID"}, status=status.HTTP_400_BAD_REQUEST)

        # Attach category to the request data and validate the serializer
        request.data["category"] = category.id  # Attach the category ID to the data
        serializer = CoursePriceSerializer(data=request.data)

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

class StudentCourseListView(ListAPIView):
    serializer_class = CourseSerializer

    def get_queryset(self):
        student_id = self.request.GET.get("studentId")  # Get student ID from query parameters

        if not student_id:
            return Course.objects.none()  # Return empty queryset if no student ID is provided

        return Course.objects.filter(sessions__student_id=student_id).distinct()
