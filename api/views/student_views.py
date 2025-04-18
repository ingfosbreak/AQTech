from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from api.permissions import IsAdmin
from api.models import User, Student
from api.serializers import StudentSerializer
from api.serializers.student_serializers import StudentListSerializer, StudentStatusUpdateSerializer
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse

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
        serializer = StudentListSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class StudentUsernameListView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdmin]

    def get(self, request):
        students = Student.objects.all()

        # Map the student objects to a list of dictionaries, including the username
        student_list = [
            {
                'id': student.id,
                'name': student.name,
                'birthdate': student.birthdate,
                'username': student.user.username,  # Get username from related User model
            }
            for student in students
        ]

        # Return the list of students with their usernames as a JSON response
        return JsonResponse(student_list, safe=False, status=status.HTTP_200_OK)

class StudentCertificateListView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdmin]

    def get(self, request):
        students = Student.objects.all()

        # Map the student objects to a list of dictionaries, including the username
        student_list = [
            {
                'id': student.id,
                'name': student.name,
                'birthdate': student.birthdate,
                'username': student.user.username,  # Get username from related User model
                'user_id': student.user.id
            }
            for student in students
        ]

        # Return the list of students with their usernames as a JSON response
        return JsonResponse(student_list, safe=False, status=status.HTTP_200_OK)


class StudentDetailView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdmin]

    def get(self, request, pk):
        try:
            storage = Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = StudentSerializer(storage)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class AddStudentView(APIView):
    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)  # Get the user
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data["user"] = user.id  # Assign user ID to student

        if user.role != "user":  # Adjust the role check based on your User model
            return Response(
                {"user": "This user does not have a user role."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = StudentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserStudentListView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        students = Student.objects.filter(user=request.user.id)
        serializer = StudentListSerializer(students, many=True)
        return Response(serializer.data)

class StudentStatusUpdateView(APIView):
    # permission_classes = [IsAuthenticated]  # Only authenticated users can access this view

    def patch(self, request, pk, *args, **kwargs):
        """
        Handle the PATCH request to update the status of a student.
        This allows changing the status to either 'active' or 'inactive'.
        """
        try:
            # Get the student instance by primary key (pk)
            student = Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return Response({"detail": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

        # Create a serializer with the student instance and the data from the request
        serializer = StudentStatusUpdateSerializer(student, data=request.data, partial=True)
        
        if serializer.is_valid():
            # If the data is valid, save the new status
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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