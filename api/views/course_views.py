from rest_framework.generics import ListAPIView
from api.models import Course
from api.models.category import Category
from api.models.session import CourseSession
from api.models.student import Student
from api.serializers.course_serializers import CourseDetailedSerializer, CourseSerializer, CoursePriceSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from api.models import Course, TeacherAssignment, Teacher, Timeslot, TimeslotTeacherAssignment
from api.serializers.session_serializers import CourseSessionSerializer
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import transaction

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
    
class CourseEnrolledView(ListAPIView):
    queryset = Course.objects.all().prefetch_related('assigns__teacher')  # Eagerly load teachers through TeacherAssignment
    serializer_class = CourseDetailedSerializer

class NewUnitCourseDetailView(APIView):
    """Admin API to get course details including assigned teachers."""

    def get(self, request, id):
        try:
            course = Course.objects.get(id=id)
        except Course.DoesNotExist:
            return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get assigned teachers
        assignments = TeacherAssignment.objects.filter(course=course)
        teachers = [
            {
                "id": assignment.teacher.id,
                "name": assignment.teacher.name,
                "contact": assignment.teacher.user.contact,
                "status": assignment.teacher.status
            }
            for assignment in assignments
        ]

        # Construct response (without enrolled, schedule, location, duration, startDate, endDate)
        data = {
            "id": course.id,
            "name": course.name,
            "description": course.description,
            "type": course.type,
            "min_age": course.min_age,
            "max_age": course.max_age,
            "quota": course.quota,
            "created_at": course.created_at.isoformat(),
            "price": course.price,
            "category": course.category.categoryName,
            "teachers": teachers,
        }

        return Response(data, status=status.HTTP_200_OK)

class NewGetAddTeacherList(APIView):
    """API to get teachers who can be added to a course (same category & not already assigned)."""

    def get(self, request, course_id):
        try:
            # Get the course
            course = Course.objects.get(id=course_id)
            
            # Get all teachers in the same category as the course
            same_category_teachers = Teacher.objects.filter(category=course.category)

            # Get teachers already assigned to the course
            assigned_teacher_ids = TeacherAssignment.objects.filter(course=course).values_list("teacher_id", flat=True)

            # Exclude assigned teachers
            available_teachers = same_category_teachers.exclude(id__in=assigned_teacher_ids)

            # Format the response
            data = [
                {
                    "id": teacher.id,
                    "name": teacher.name,
                    "contact": teacher.user.contact,
                    "status": teacher.status
                }
                for teacher in available_teachers
            ]

            return Response(data, status=status.HTTP_200_OK)

        except Course.DoesNotExist:
            return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

class NewAddTeacherToCourse(APIView):
    """API to assign a teacher to a course if they are not already assigned."""

    def post(self, request, course_id):
        try:
            # Get course
            course = Course.objects.get(id=course_id)
            teacher_id = request.data.get("teacher_id")

            if not teacher_id:
                return Response({"error": "teacher_id is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Get teacher
            try:
                teacher = Teacher.objects.get(id=teacher_id)
            except Teacher.DoesNotExist:
                return Response({"error": "Teacher not found"}, status=status.HTTP_404_NOT_FOUND)

            # Check if teacher belongs to the same category
            if teacher.category != course.category:
                return Response(
                    {"error": "Teacher's category does not match the course category"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if teacher is already assigned
            if TeacherAssignment.objects.filter(course=course, teacher=teacher).exists():
                return Response({"error": "Teacher is already assigned to this course"}, status=status.HTTP_400_BAD_REQUEST)

            # Assign teacher to course
            TeacherAssignment.objects.create(course=course, teacher=teacher)

            today = timezone.now().date()
            timeslots = Timeslot.objects.filter(course=course, timeslot_date__gte=today)
            for timeslot in timeslots:
                    if not TimeslotTeacherAssignment.objects.filter(timeslot=timeslot, teacher=teacher).exists():
                        TimeslotTeacherAssignment.objects.create(timeslot=timeslot, teacher=teacher)

            return Response({"message": "Teacher assigned successfully"}, status=status.HTTP_201_CREATED)

        except Course.DoesNotExist:
            return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
        
class NewRemoveTeacherFromCourse(APIView):
    """API to remove a teacher from a course."""

    def delete(self, request, course_id, teacher_id):
        try:
            with transaction.atomic():  # ✅ ทำให้การลบข้อมูลเป็น Atomic Transaction
                # ✅ ดึงข้อมูลคอร์ส
                course = Course.objects.get(id=course_id)
                
                # ✅ ดึงข้อมูลอาจารย์
                try:
                    teacher = Teacher.objects.get(id=teacher_id)
                except Teacher.DoesNotExist:
                    return Response({"error": "Teacher not found"}, status=status.HTTP_404_NOT_FOUND)

                # ✅ เช็คว่าอาจารย์ถูก assign ไว้ในคอร์สหรือไม่
                teacher_assignment = TeacherAssignment.objects.filter(course=course, teacher=teacher)
                if not teacher_assignment.exists():
                    return Response({"error": "Teacher is not assigned to this course"}, status=status.HTTP_400_BAD_REQUEST)

                # ✅ ลบอาจารย์ออกจากคอร์ส
                teacher_assignment.delete()

                return Response({"message": "Teacher removed successfully"}, status=status.HTTP_200_OK)

        except Course.DoesNotExist:
            return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)