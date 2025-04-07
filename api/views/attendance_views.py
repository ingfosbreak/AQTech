from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from api.permissions import IsAdmin
from api.models import Attendance, CourseSession, Student, Course
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from django.forms.models import model_to_dict
from django.db.models import Prefetch
import urllib.parse

class AttendanceView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdmin]

    def post(self, request):
        session_id = request.data.get("session_id")
        date_str = request.data.get("date")
        start_time_str = request.data.get('start_time')
        
        if not session_id:
            return JsonResponse({"error": "Missing required parameters."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            session = CourseSession.objects.get(id=session_id)
        except CourseSession.DoesNotExist:
            return JsonResponse({"error": "session not found."}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            decoded_date_str = urllib.parse.unquote(date_str)
            date_obj = timezone.datetime.strptime(decoded_date_str, "%Y-%m-%dT%H:%M:%S.%fZ").date()
            start_time = datetime.strptime(start_time_str, "%I:%M %p").time()  # Parse start time
        except ValueError as e:
            return JsonResponse({"error": e}, status=status.HTTP_400_BAD_REQUEST)
        
        today = timezone.localtime().date()
        now = timezone.localtime()
        start_datetime = datetime.combine(date_obj, start_time)
        start_datetime = timezone.make_aware(start_datetime, timezone.get_current_timezone())
        end_datetime = start_datetime + timedelta(hours=1)
        end_time = end_datetime.time()

        if date_obj < today:
            return JsonResponse({"error": "The date must be today or in the future."}, status=status.HTTP_400_BAD_REQUEST)
        
        if date_obj == today:
            # Check if current time is before or up to the start time of the session
            if now > start_datetime:
                return JsonResponse({"error": "The start time has passed, attendance can no longer be marked."}, status=status.HTTP_400_BAD_REQUEST)

        existing_attendance = Attendance.objects.filter(
            session=session,
            attendance_date=date_obj,
            start_time=start_time
        ).first()

        if existing_attendance:
            return JsonResponse({"error": "Attendance for today has already been recorded."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create the attendance record
            attendance = Attendance.objects.create(
                status="absent",
                session=session,
                student=session.student,
                teacher=session.teacher,
                attendance_date=date_obj,
                start_time=start_time,
                end_time=end_time,
            )

        except Exception as e:
            # Log the exception and return an error
            print(f"Error creating attendance: {e}")  # Log error to console
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return JsonResponse(model_to_dict(attendance), safe=False, status=status.HTTP_200_OK)

class AttendanceModifyView(APIView):

    def get(self, request):
        try:
            # Prefetch related sessions and attendances for each student
            attendances_prefetch = Prefetch('attendances', queryset=Attendance.objects.all(), to_attr='attendances_list')

            # Load students and prefetch their sessions and attendances
            students = Student.objects.prefetch_related(
                Prefetch('sessions', queryset=CourseSession.objects.all().prefetch_related(attendances_prefetch), to_attr='sessions_list')
            ).all()

            # Prepare response data
            result = []
            for student in students:
                student_data = model_to_dict(student)
                student_data['username'] = student.user.username
                student_data['sessions'] = []
                
                for session in student.sessions_list:
                    session_data = model_to_dict(session)
                    session_data['session_name'] = session.course.name
                    session_data['attendances'] = []

                    # Map attendance to each session
                    for attendance in session.attendances_list:
                        session_data['attendances'].append(model_to_dict(attendance))

                    student_data['sessions'].append(session_data)

                result.append(student_data)

            return Response(result, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": f"Something went wrong: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateAttendanceStatus(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdmin]

    def patch(self, request):
        student_id = request.data.get('student_id')
        
        # Get the current date and time
        current_time = timezone.now().replace(microsecond=0)
        current_date = current_time.date()

        if not student_id:
            return Response({'detail': 'student_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Filter attendances by student_id, today's date, and time between start_time and end_time
        attendance = Attendance.objects.filter(
            student_id=student_id,
            attendance_date=current_date,
            status='absent'  # Only update if the student is marked as 'absent'
        ).first()  # Get the first match (or None if no match)

        if not attendance:
            return Response({'detail': 'No matching attendance found for the student at this time.'}, status=status.HTTP_400_BAD_REQUEST)


        start_datetime = datetime.combine(attendance.attendance_date, attendance.start_time)
        end_datetime = datetime.combine(attendance.attendance_date, attendance.end_time)
        
        # Make the datetime objects timezone-aware
        start_datetime = timezone.make_aware(start_datetime, timezone.get_current_timezone())
        end_datetime = timezone.make_aware(end_datetime, timezone.get_current_timezone())

        if start_datetime <= current_time <= end_datetime:
            # Update the attendance status to 'present' and set the checked_date to now
            attendance.status = 'present'
            attendance.checked_date = current_time
            attendance.save()

            return Response({'detail': 'Attendance updated successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Current time is not within the attendance session period.'}, status=status.HTTP_400_BAD_REQUEST)

class AttendanceListView(APIView):
    def get(self, request):
        student_id = request.GET.get("student_id")
        course_id = request.GET.get("course_id")

        if not student_id or not course_id:
            return Response({"error": "student_id and course_id are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # หา Student
            student = Student.objects.get(id=student_id)

            # 1️⃣ ดึง Attendance ทั้งหมดของ Student
            all_attendances = Attendance.objects.filter(student=student)

             # 2️⃣ หา CourseSession ที่มี Course ตรงกับ `course_type`
            course = Course.objects.get(id=course_id)
            course_type = course.type

            type_attendances = Attendance.objects.filter(session__course__type=course_type)

            unique_attendances = {}
            for att in list(all_attendances) + list(type_attendances):
                if att.id not in unique_attendances:
                    unique_attendances[att.id] = {
                        "id": att.id,
                        "status": att.status,
                        "session_id": att.session.id,
                        "session_date": att.session.session_date,
                        "course_id": att.session.course.id,
                        "course_name": att.session.course.name,
                        "teacher_id": att.teacher.id,
                        "teacher_name": f"{att.teacher.name}",
                        "student_id": att.student.id,
                        "student_name": f"{att.student.name}",
                        "attendance_date": att.attendance_date,
                        "start_time": att.start_time,
                        "end_time": att.end_time,
                        "is_owner": att.student.id == int(student_id)
                    }
            
            return JsonResponse(list(unique_attendances.values()), safe=False, status=status.HTTP_200_OK)
        
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
        except Course.DoesNotExist:
            return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AttendanceListModifyView(APIView):
    def get(self, request):
        student_id = request.GET.get("student_id")
        session_id = request.GET.get("session_id")

        if not student_id or not session_id:
            return Response({"error": "student_id and session_id are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # หา Student
            student = Student.objects.get(id=student_id)

            # 1️⃣ ดึง Attendance ทั้งหมดของ Student
            all_attendances = Attendance.objects.filter(student=student)

             # 2️⃣ หา CourseSession ที่มี Course ตรงกับ `course_type`
            course = CourseSession.objects.get(id=session_id)
            course_type = course.course.type

            type_attendances = Attendance.objects.filter(session__course__type=course_type)

            unique_attendances = {}
            for att in list(all_attendances) + list(type_attendances):
                if att.id not in unique_attendances:
                    unique_attendances[att.id] = {
                        "id": att.id,
                        "status": att.status,
                        "session_id": att.session.id,
                        "session_date": att.session.session_date,
                        "course_id": att.session.course.id,
                        "course_name": att.session.course.name,
                        "teacher_id": att.teacher.id,
                        "teacher_name": f"{att.teacher.name}",
                        "student_id": att.student.id,
                        "student_name": f"{att.student.name}",
                        "attendance_date": att.attendance_date,
                        "start_time": att.start_time,
                        "end_time": att.end_time,
                        "is_owner": att.student.id == int(student_id)
                    }
            
            return JsonResponse(list(unique_attendances.values()), safe=False, status=status.HTTP_200_OK)
        
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
        except CourseSession.DoesNotExist:
            return Response({"error": "CourseSession not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

