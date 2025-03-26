from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from api.permissions import IsAdmin
from api.models import User, Teacher
from api.serializers import TeacherSerializer, UserSerializer
from django.db import transaction
from django.http import JsonResponse

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

class CreateUserTeacherView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdmin]

    @transaction.atomic
    def post(self, request):
        user_data = {
            "first_name": request.data.get("first_name"),
            "last_name": request.data.get("last_name"),
            "username": request.data.get("username"),
            "password": request.data.get("password"),
            "contact": request.data.get("contact"),
            "role": "teacher"  # Ensure the user is always a teacher
        }

        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            user = user_serializer.save()

            # Prevent duplicate teacher assignment
            if Teacher.objects.filter(user_id=user.id).exists():
                transaction.set_rollback(True)
                return Response(
                    {"user": "This user is already assigned as a teacher."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            teacher_data = {"user": user.id, "name": f"{user.first_name} {user.last_name}"}
            teacher_serializer = TeacherSerializer(data=teacher_data)

            # Create Teacher entry
            if teacher_serializer.is_valid():
                teacher_serializer.save()

                return Response(
                    {
                        "message": "user created"
                    },
                    status=status.HTTP_201_CREATED,
                )

            transaction.set_rollback(True)
            return Response(teacher_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class TeacherListView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdmin]

    def get(self, request):
        teachers = Teacher.objects.all()
        serializer = TeacherSerializer(teachers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class TeacherUsernameListView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdmin]

    def get(self, request):
        teachers = Teacher.objects.all()

        teacher_list = [
            {
                'id': teacher.id,
                'name': teacher.name,
                'username': teacher.user.username,  # Get username from related User model
            }
            for teacher in teachers
        ]

        return JsonResponse(teacher_list, safe=False, status=status.HTTP_200_OK)
    
class TeacherDetailView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdmin]

    def get(self, request, teacher_id):
        try:
            teacher = Teacher.objects.get(id=teacher_id)
            teacher_data = {
                'id': teacher.id,
                'name': teacher.name,
                'username': teacher.user.username,  # Get username from related User model
                'sessions': [
                    {
                        'session_id': session.id,
                        'course': session.course.name,
                        'session_date': session.session_date,
                        'start_time': session.start_time,
                        'end_time': session.end_time,
                        'total_quota': session.total_quota,
                    }
                    for session in teacher.sessions.all()
                ]
            }
            return JsonResponse(teacher_data, safe=False, status=status.HTTP_200_OK)

        except Teacher.DoesNotExist:
            return JsonResponse({'error': 'Teacher not found'}, status=status.HTTP_404_NOT_FOUND)
