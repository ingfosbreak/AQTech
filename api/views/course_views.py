from rest_framework.generics import ListAPIView
from api.models import Course
from api.models.category import Category
from api.models.session import CourseSession
from api.models.student import Student
from api.models.receipt import Receipt  
from api.serializers.course_serializers import CourseDetailedSerializer, CourseSerializer, CoursePriceSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from api.models import Course, TeacherAssignment, Teacher, Timeslot, TimeslotTeacherAssignment, Attendance
from api.serializers.session_serializers import CourseSessionSerializer
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import transaction
from django.http import JsonResponse
from datetime import datetime, time
from django.utils.timezone import now

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
    """Admin API to get course details including assigned teachers and sessions."""

    def get(self, request, id):
        try:
            # Get the course by its ID
            course = Course.objects.get(id=id)
        except Course.DoesNotExist:
            return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get assigned teachers for the course
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

        # Get sessions for the course
        sessions = CourseSession.objects.filter(course=course)
        session_data = []
        for session in sessions:
            # Get all attendances for this session
            attendances = Attendance.objects.filter(session=session)

            attendance_data = []
            for attendance in attendances:
                # Assuming each attendance record has a related student (attendance.student)
                attendance_data.append({
                    "id": attendance.id,
                    "status": attendance.status,
                    "type": attendance.type,
                    "student_id": attendance.student.id,
                    "student_name": attendance.student.name,
                    "attendance_date": attendance.attendance_date,
                    "start_time": attendance.start_time,
                    "end_time": attendance.end_time,
                    "checked_date": attendance.checked_date  # Add checked_date here
                })

            # Only include sessions that have attendances
            if attendance_data:
                session_data.append({
                    "id": session.id,
                    "name": session.name,
                    "total_quota": session.total_quota,
                    "attendances": attendance_data
                })

        # Construct the response data for the course, including teachers and sessions
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
            "sessions": session_data  # Add the sessions data
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

class NewCreateCourseAPIView(APIView):
    """API to create a new course"""

    def post(self, request):
        try:
            data = request.data

            # Validate required fields
            required_fields = ["name", "description", "type", "quota", "price", "category_id"]
            for field in required_fields:
                if field not in data:
                    return Response({"error": f"{field} is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Validate course type
            if data["type"] not in ["restricted", "unrestricted"]:
                return Response({"error": "Invalid course type"}, status=status.HTTP_400_BAD_REQUEST)

            # If type is 'restricted', min_age and max_age are required
            if data["type"] == "restricted":
                if "min_age" not in data or "max_age" not in data:
                    return Response({"error": "min_age and max_age are required for restricted courses"}, status=status.HTTP_400_BAD_REQUEST)

                if data["min_age"] is None or data["max_age"] is None:
                    return Response({"error": "min_age and max_age cannot be null for restricted courses"}, status=status.HTTP_400_BAD_REQUEST)

                if data["min_age"] > data["max_age"]:
                    return Response({"error": "min_age cannot be greater than max_age"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # If type is 'unrestricted', min_age and max_age should be set to None
                data["min_age"] = None
                data["max_age"] = None

            # Validate category exists
            try:
                category = Category.objects.get(id=data["category_id"])
            except Category.DoesNotExist:
                return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

            # Create course
            course = Course.objects.create(
                name=data["name"],
                description=data["description"],
                type=data["type"],
                min_age=data["min_age"],
                max_age=data["max_age"],
                quota=data["quota"],
                price=data["price"],
                category=category,
                created_at=timezone.now()
            )

            return Response({"message": "Course created successfully", "course_id": course.id}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class NewUnitCourseListView(APIView):
    """Admin API to get list of all courses including assigned teachers."""

    def get(self, request):
        courses = Course.objects.all().select_related("category").prefetch_related("assigns__teacher__user")
        response_data = []

        for course in courses:
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

            response_data.append({
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
            })

        return Response(response_data, status=status.HTTP_200_OK)

class NewStudentUsernameListView(APIView):
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
                'username': student.user.username,
                "avatar": "/placeholder.svg?height=64&width=64",
            }
            for student in students
        ]

        # Return the list of students with their usernames as a JSON response
        return JsonResponse(student_list, safe=False, status=status.HTTP_200_OK)

class TimeSlotSelectionView(APIView):
    """
    API that returns:
    1. course_timeslots: Available timeslots for the given course
    2. other_category_timeslots: Timeslots from other courses in the same category (for reference)
    3. student_attendances: All future attendances of the given students
    """

    def post(self, request):
        course_id = request.data.get("courseId")
        student_ids = request.data.get("studentIds", [])

        if not course_id or not student_ids:
            return Response({"error": "courseId and studentIds are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

        today = timezone.localdate()

        # 1. Determine quota per category
        def get_quota_for_category(category_name):
            if category_name.lower() == "playsound":
                return 2
            return 6  # both aquakids and other

        course_category = course.category.categoryName
        category_quota = get_quota_for_category(course_category)

        # 2. Timeslots of current course (from today onwards)
        course_timeslots = Timeslot.objects.filter(course=course, timeslot_date__gte=today)

        course_timeslot_data = []
        for ts in course_timeslots:
            current_attendance = Attendance.objects.filter(timeslot=ts).count()
            available_quota = category_quota - current_attendance
            course_timeslot_data.append({
                "id": ts.id,
                "date": ts.timeslot_date.isoformat(),
                "startTime": ts.start_time.strftime("%H:%M") if ts.start_time else None,
                "endTime": ts.end_time.strftime("%H:%M") if ts.end_time else None,
                "hour": ts.start_time.hour if ts.start_time else None,
                "availableQuota": available_quota,
                "courseId": str(course.id),
                "courseName": course.name,
                "isNewSlot": False,
            })

        # 3. Timeslots of other courses in same category
        other_courses = Course.objects.filter(category=course.category).exclude(id=course.id)
        other_timeslots = Timeslot.objects.filter(course__in=other_courses, timeslot_date__gte=today)

        other_timeslot_data = []
        for ts in other_timeslots:
            other_course = ts.course
            other_quota = get_quota_for_category(other_course.category.categoryName)
            current_attendance = Attendance.objects.filter(timeslot=ts).count()
            available_quota = other_quota - current_attendance
            other_timeslot_data.append({
                "id": ts.id,
                "date": ts.timeslot_date.isoformat(),
                "startTime": ts.start_time.strftime("%H:%M") if ts.start_time else None,
                "endTime": ts.end_time.strftime("%H:%M") if ts.end_time else None,
                "hour": ts.start_time.hour if ts.start_time else None,
                "availableQuota": available_quota,
                "courseId": str(other_course.id),
                "courseName": other_course.name,
                "isNewSlot": False,  # Always true since same category
            })

        # 4. Student attendance records (future only)
        student_attendance_data = []
        for sid in student_ids:
            try:
                student = Student.objects.get(id=sid)
            except Student.DoesNotExist:
                continue

            attendances = Attendance.objects.filter(
                student=student,
                attendance_date__gte=today
            ).select_related("timeslot", "timeslot__course")

            timeslots = []
            for att in attendances:
                ts = att.timeslot
                related_course = ts.course
                related_quota = get_quota_for_category(related_course.category.categoryName)
                current_attendance = Attendance.objects.filter(timeslot=ts).count()
                available_quota = related_quota - current_attendance

                timeslots.append({
                    "id": ts.id,
                    "date": ts.timeslot_date.isoformat(),
                    "startTime": ts.start_time.strftime("%H:%M") if ts.start_time else None,
                    "endTime": ts.end_time.strftime("%H:%M") if ts.end_time else None,
                    "hour": ts.start_time.hour if ts.start_time else None,
                    "availableQuota": available_quota,
                    "courseId": str(related_course.id),
                    "courseName": related_course.name,
                    "isNewSlot": False,
                    "isSameCourse": ts.course.category.categoryName == course.category.categoryName
                })

            student_attendance_data.append({
                "studentId": sid,
                "timeslots": timeslots
            })

        return Response({
            "course_timeslots": course_timeslot_data,
            "other_category_timeslots": other_timeslot_data,
            "student_attendances": student_attendance_data,
        }, status=status.HTTP_200_OK)
    
class CreateBatchAttendanceAPIView(APIView):
    def post(self, request):
        try:
            data = request.data
            bookings = data.get("bookings", [])
            course_id = data.get("course_id")

            if not course_id:
                return Response({"error": "course_id is required"}, status=status.HTTP_400_BAD_REQUEST)

            course = Course.objects.get(id=course_id)

            # ✅ Get all assigned teachers for this course
            assigned_teachers = TeacherAssignment.objects.filter(course=course)
            if not assigned_teachers.exists():
                return Response({"error": "No teacher assigned to this course"}, status=status.HTTP_400_BAD_REQUEST)

            # ✅ Use the first teacher for attendance record (just to fill required field)
            default_teacher = assigned_teachers.first().teacher

            today = timezone.localdate()
            created_attendance_ids = []

            with transaction.atomic():

                # ✅ เตรียม student set ล่วงหน้า
                all_student_ids = set()
                for booking in bookings:
                    all_student_ids.update(booking["studentIds"])

                # ✅ สร้าง CourseSession และ Receipt ให้แต่ละ student (1 ครั้ง)
                student_session_map = {}

                for student_id in all_student_ids:
                    student = Student.objects.get(id=student_id)
                    session_name = f"Session-{student.id}-{course.id}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
                    session = CourseSession.objects.create(
                        course=course,
                        student=student,
                        name=session_name,
                        total_quota=course.quota
                    )
                        # ✅ สร้าง Receipt
                    current_year = timezone.now().year
                    last_receipt = Receipt.objects.filter(receipt_number__startswith=f"INV-{current_year}") \
                        .order_by("-receipt_number").first()

                    if last_receipt:
                        last_number = int(last_receipt.receipt_number.split("-")[-1])
                    else:
                        last_number = 0
                    next_number = last_number + 1
                    receipt_number = f"INV-{current_year}-{str(next_number).zfill(5)}"

                    Receipt.objects.create(
                        student=student,
                        session=session,
                        amount=course.price,
                        receipt_number=receipt_number,
                        payment_method="CARD",
                        notes=f"Payment for {course.name}",
                        items=[{
                            "description": "Course Registration Fee",
                            "amount": course.price
                        }],
                        payment_date=now(),   
                        created_at=now(),
                    )

                    student_session_map[student_id] = session
                
                for booking in bookings:
                    date_str = booking["date"]
                    start_time_str = booking["startTime"]
                    student_ids = booking["studentIds"]
                    is_new = booking.get("isNewSlot", False)

                    booking_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    booking_start = datetime.strptime(start_time_str, "%H:%M").time()
                    booking_end = time(booking_start.hour + 1, 0)

                    if is_new:
                        # ✅ Create new timeslot
                        timeslot = Timeslot.objects.create(
                            course=course,
                            timeslot_date=booking_date,
                            start_time=booking_start,
                            end_time=booking_end
                        )

                        # ✅ Assign all teachers to the timeslot
                        for assign in assigned_teachers:
                            TimeslotTeacherAssignment.objects.create(
                                timeslot=timeslot,
                                teacher=assign.teacher
                            )

                    else:
                        timeslot_id = booking.get("id")
                        if not timeslot_id:
                            return Response({"error": "Missing timeslot id for existing slot"}, status=status.HTTP_400_BAD_REQUEST)

                        try:
                            timeslot = Timeslot.objects.get(id=timeslot_id)
                        except Timeslot.DoesNotExist:
                            return Response({"error": f"Timeslot id {timeslot_id} not found for course"}, status=status.HTTP_404_NOT_FOUND)

                    for student_id in student_ids:
                        student = Student.objects.get(id=student_id)
                        session = student_session_map[student_id]
                        # ✅ Create attendance record
                        att = Attendance.objects.create(
                            status="absent",
                            type="scheduled",
                            session=session,
                            student=student,
                            teacher=default_teacher,  # placeholder teacher (required field)
                            timeslot=timeslot,
                            attendance_date=booking_date,
                            start_time=booking_start,
                            end_time=booking_end
                        )
                        created_attendance_ids.append(att.id)

            return Response({
                "message": "Attendances created successfully",
                "count": len(created_attendance_ids),
                "attendance_ids": created_attendance_ids
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AttendanceDetailsList(APIView):
    def post(self, request):
        # Get the list of attendance IDs from the request
        attendance_ids = request.data.get('ids', [])
        
        # Validate if IDs are provided
        if not attendance_ids:
            return Response({"error": "No attendance IDs provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Fetch the attendance records with the provided IDs
        attendances = Attendance.objects.filter(id__in=attendance_ids)
        
        # If no attendances are found
        if not attendances:
            return Response({"error": "No attendances found for the provided IDs"}, status=status.HTTP_404_NOT_FOUND)
        
        # Serialize the attendance data
        attendance_data = [
            {
                "id": att.id,
                "status": att.status,
                "type": att.type,
                "session": att.session.id,
                "student": att.student.id,
                "timeslot": att.timeslot.id,
                "attendance_date": att.attendance_date.strftime('%Y-%m-%d'),
                "start_time": att.start_time.strftime('%H:%M'),
                "end_time": att.end_time.strftime('%H:%M')
            }
            for att in attendances
        ]

        # Return the serialized data in the response
        return Response({"attendances": attendance_data}, status=status.HTTP_200_OK)