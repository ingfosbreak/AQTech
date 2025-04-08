from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from api.models.attendance import Attendance
from api.models.course import Course
from api.models.session import CourseSession
from api.permissions import IsAdmin
from api.models import User, Teacher, Category, TeacherAssignment
from django.contrib.auth.hashers import make_password
from api.serializers import TeacherSerializer, UserSerializer
from django.db import transaction
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated

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
            "role": "teacher",  # Ensure the user is always a teacher
            "status": request.data.get("status"),

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
    
class NewCreateTeacherUserView(APIView):
    
    @transaction.atomic
    def post(self, request):
        try:
            # Extract user data from request
            first_name = request.data.get("first_name")
            last_name = request.data.get("last_name")
            username = request.data.get("username")
            password = request.data.get("password")
            contact = request.data.get("contact")
            category_id = request.data.get("category")  # Expecting category ID
            status_value = request.data.get("status", "active")

            # Validate required fields
            if not all([first_name, last_name, username, password, category_id, contact]):
                return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

            # Ensure category exists
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                return Response({"error": "Invalid category ID"}, status=status.HTTP_400_BAD_REQUEST)

            # Create User
            user = User.objects.create(
                first_name=first_name,
                last_name=last_name,
                username=username,
                password=make_password(password),  # Hash password for security
                contact=contact,
                role="teacher",  # Set role as 'teacher'
            )

            # Ensure user isn't already assigned as a teacher
            if Teacher.objects.filter(user=user).exists():
                transaction.set_rollback(True)
                return Response(
                    {"error": "This user is already assigned as a teacher."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Create Teacher
            Teacher.objects.create(
                user=user,
                category=category,
                status=status_value,
                name=f"{first_name} {last_name}"
            )

            return Response({"message": "User and teacher created successfully"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            transaction.set_rollback(True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

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
                        'course': session.course.courseName,
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

class TeacherStatusUpdateView(APIView):
    def patch(self, request, pk):
        try:
            teacher = Teacher.objects.get(pk=pk)
        except Teacher.DoesNotExist:
            return Response({"detail": "Teacher not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Get the new status from the request
        new_status = request.data.get("status")
        
        # Validate the status
        if new_status not in ['active', 'inactive']:
            return Response({"detail": "Invalid status value"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update the teacher's status
        teacher.status = new_status
        teacher.save()

        # Return the updated teacher data
        serializer = TeacherSerializer(teacher)
        return Response(serializer.data, status=status.HTTP_200_OK)

class NewTeacherDetailView(APIView):
    
    def get(self, request, id):
        try:
            teacher = Teacher.objects.get(id=id)
        except Teacher.DoesNotExist:
            return Response({"error": "Teacher not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get assigned courses
        assignments = TeacherAssignment.objects.filter(teacher=teacher)
        classes = [
            {
                "id": assignment.course.id,
                "name": assignment.course.name,
                "description": assignment.course.description,
                "type": assignment.course.type,
                "min_age": assignment.course.min_age,
                "max_age": assignment.course.max_age,
            }
            for assignment in assignments
        ]

        # Construct response
        data = {
            "id": teacher.id,
            "name": teacher.name,
            "contact": teacher.user.contact,
            "category": teacher.category.categoryName,
            "status": teacher.status,
            "classes": classes,
        }

        return Response(data, status=status.HTTP_200_OK)
    
class TeacherAssignmentView(APIView):
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        # Ensure the user is a teacher
        user = request.user

        if user.role != 'teacher':
            return Response(
                {"error": "Forbidden: User is not a teacher"},
                status=403
            )

        teacher = request.user.teachers  # Get the teacher object linked to the user

        # Get assigned courses
        assignments = TeacherAssignment.objects.filter(teacher=teacher)
        classes = [
            {
                "id": assignment.course.id,
                "name": assignment.course.name,
                "description": assignment.course.description,
                "type": assignment.course.type,
                "min_age": assignment.course.min_age,
                "max_age": assignment.course.max_age,
            }
            for assignment in assignments
        ]

        # Construct response
        data = {
            "id": teacher.id,
            "name": teacher.name,
            "contact": teacher.user.contact,
            "category": teacher.category.categoryName,
            "status": teacher.status,
            "classes": classes,
        }

        return Response(data, status=status.HTTP_200_OK)

class TeacherProfileView(APIView):
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        user = request.user

        if user.role != 'teacher':
            return Response(
                {"error": "Forbidden: User is not a teacher"},
                status=403
            )

        teacher = get_object_or_404(Teacher, user=user)

        # Serialize both the teacher and user
        teacher_serializer = TeacherSerializer(teacher)
        user_serializer = UserSerializer(user)

        # Combine the data into one dictionary
        data = {
            'user': user_serializer.data,
            'teacher': teacher_serializer.data
        }

        return Response(data)
    
class ClassSessionView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]  # Ensure user is authenticated

    def get(self, request, class_id):
        # Ensure the user is a teacher
        user = request.user

        if user.role != 'teacher':
            return Response(
                {"error": "Forbidden: User is not a teacher"},
                status=403
            )

        # Get the course by ID (class_id)
        try:
            course = Course.objects.get(id=class_id)
        except Course.DoesNotExist:
            return Response(
                {"error": "Course not found"},
                status=404
            )

        # Get all sessions related to the course
        sessions = CourseSession.objects.filter(course=course)

        session_data = []
        for session in sessions:
            # Get all attendances for this session
            attendances = Attendance.objects.filter(session=session)

            attendance_data = []
            for attendance in attendances:
                # Check if the attendance's student_id matches the session's student_id
                # Assuming each CourseSession has a related student (e.g., session.student)
                if attendance.student.id == session.student.id:  # Match student ID
                    attendance_data.append({
                        "id": attendance.id,
                        "status": attendance.status,
                        "type": attendance.type,
                        "student_id": attendance.student.id,
                        "student_name": attendance.student.name,
                        "attendance_date": attendance.attendance_date,
                        "start_time": attendance.start_time,
                        "end_time": attendance.end_time,
                    })

            # Only include sessions that have matching attendance records
            if attendance_data:
                session_data.append({
                    "id": session.id,
                    "name": session.name,
                    "total_quota": session.total_quota,
                    "attendances": attendance_data
                })

        # If no sessions have matching attendance data, return an error message
        if not session_data:
            return Response(
                {"error": "No students enrolled in this class or no sessions available."},
                status=404
            )

        # Construct response data for the teacher
        data = {
            "course_id": course.id,
            "course_name": course.name,
            "sessions": session_data
        }

        return Response(data, status=status.HTTP_200_OK)