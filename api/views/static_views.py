from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from api import models
from api.models import Student, Teacher, CourseSession
from django.utils.timezone import now
from datetime import timedelta
from datetime import time
from django.utils.timezone import localtime
from django.db.models import Q

from api.models.attendance import Attendance

class CombinedCountView(APIView):
    def get(self, request):
        # Total number of students
        total_student = Student.objects.count()

        # Active students (students with at least one ongoing session)
        active_student = Student.objects.filter(
            sessions__course__sessions__end_time__gte=now()
        ).distinct().count()

        # Inactive students (students who have no ongoing sessions)
        inactive_student = total_student - active_student

        # New students (students created in the last 30 days)
        thirty_days_ago = now() - timedelta(days=30)
        new_students = Student.objects.filter(user__date_joined__gte=thirty_days_ago).count()

        return Response(
            {
                "totalStudent": total_student,
                "activeStudent": active_student,
                "inactiveStudent": inactive_student,
                "newStudents": new_students
            },
            status=status.HTTP_200_OK
        )

class PieChartStaticView(APIView):
    def get(self, request):
        student_count = Student.objects.aggregate(count=Count('id'))['count']
        teacher_count = Teacher.objects.aggregate(count=Count('id'))['count']

        data = [
            {"name": "Student", "value": student_count},
            {"name": "Teacher", "value": teacher_count}
        ]

        return Response(data, status=status.HTTP_200_OK)

class AttendanceHeatmapView(APIView):
    def get(self, request):
        course_type = request.GET.get("courseType", "All")

        # Define time slot ranges
        time_slots = {
            "9am": (time(9, 0), time(11, 0)),
            "11am": (time(11, 0), time(13, 0)),
            "1pm": (time(13, 0), time(15, 0)),
            "3pm": (time(15, 0), time(17, 0)),
            "5pm": (time(17, 0), time(19, 0)),
        }
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        # Filter sessions based on course type
        if course_type != "All":
            sessions = CourseSession.objects.filter(course__type__typeName=course_type)
        else:
            sessions = CourseSession.objects.all()  # ✅ Ensure `sessions` is always assigned

        # Prepare empty heatmap structure
        heatmap_data = {day: {slot: 0 for slot in time_slots.keys()} for day in days}

        for session in sessions:
            session_day = session.session_date.strftime("%a")[:3]  # Convert date to "Mon", "Tue", etc.
            if session_day not in days:
                continue

            # Total students for this session
            total_students = Attendance.objects.filter(session=session).count()
            if total_students == 0:
                continue  # Skip if no students

            for slot, (start_time, end_time) in time_slots.items():
                # Count students who attended in this time slot
                attended_students = Attendance.objects.filter(
                    session=session,
                    status="present",
                    start_time__gte=start_time,
                    end_time__lte=end_time,
                ).count()

                # Calculate attendance percentage
                attendance_percentage = (attended_students / total_students) * 100
                heatmap_data[session_day][slot] = round(attendance_percentage, 2)

        return Response(heatmap_data, status=status.HTTP_200_OK)


class AttendanceLogView(APIView):
    def get(self, request):
        search_term = request.GET.get("search", "").strip().lower()
        sort_newest_first = request.GET.get("sortNewestFirst", "true").lower() == "true"

        queryset = Attendance.objects.select_related("session__course__type", "student").all()

        # Apply search filter
        if search_term:
            queryset = queryset.filter(
                Q(student__name__icontains=search_term) |
                Q(session__course__courseName__icontains=search_term) |
                Q(session__course__type__typeName__icontains=search_term) |
                Q(checked_date__icontains=search_term)  # Updated from 'timestamp' to 'checked_date'
            )

        # Apply sorting
        if sort_newest_first:
            queryset = queryset.order_by("-checked_date")  # Updated from 'timestamp' to 'checked_date'
        else:
            queryset = queryset.order_by("checked_date")

        # Serialize data
        records = [
            {
                "id": attendance.id,
                "name": attendance.student.name,
                "course": attendance.session.course.courseName,
                "courseType": attendance.session.course.type.typeName,
                "timestamp": localtime(attendance.checked_date).strftime("%Y-%m-%d %H:%M:%S"),  # Updated field
            }
            for attendance in queryset
        ]

        return Response(records, status=status.HTTP_200_OK)
