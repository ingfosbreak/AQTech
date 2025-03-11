from rest_framework.generics import ListAPIView
from api.models import Course
from api.serializers.course_serializers import CourseSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from api.models import Course, Level

class CourseListView(ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

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