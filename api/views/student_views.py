from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from api.permissions import IsAdmin
from api.models import User, Student
from api.serializers import StudentSerializer

class StudentCreateView(APIView):
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
        
         # Check if the user's role is "user"
        if user.role != "user":  # Adjust the role check based on your User model
            return Response(
                {"user": "This user does not have a user role."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentListView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdmin]

    def get(self, request):
        students = Student.objects.all()
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
# class StudentCountView(APIView):
#     def get(self, request):
#         active_students = Student.objects.filter(is_active=True).count()
#         inactive_students = Student.objects.filter(is_active=False).count()
#         total_students = Student.objects.count()

#         return Response(
#             {
#                 "total_students": total_students,
#                 "active_students": active_students,
#                 "inactive_students": inactive_students,
#             },
#             status=status.HTTP_200_OK,
#         )