from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from api.permissions import IsAdmin
from api.models import User, Teacher
from api.serializers import TeacherSerializer

class TeacherCreateView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdmin]

    def post(self, request):

        user_id = request.data.get("user")
        # Ensure user exists
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"user": "User not found."}, status=status.HTTP_400_BAD_REQUEST
            )
        
         # Check if the user's role is "teacher"
        if user.role != "teacher":  # Adjust the role check based on your User model
            return Response(
                {"user": "This user does not have a teacher role."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Prevent duplicate teacher assignment
        if Teacher.objects.filter(user_id=user_id).exists():
            return Response(
                {"user": "This user is already assigned as a teacher."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = TeacherSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TeacherListView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdmin]

    def get(self, request):
        teachers = Teacher.objects.all()
        serializer = TeacherSerializer(teachers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
