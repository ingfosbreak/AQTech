from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, DateField
from api import models
from api.models import Student, Teacher, CourseSession
from django.utils.timezone import now
from datetime import timedelta
from datetime import time
from django.utils.timezone import localtime, get_current_timezone
from django.db.models import Q
from django.utils import timezone
from api.models.attendance import Attendance
from api.models import Attendance
from django.db.models.functions import TruncDate
from django.db.models.functions import ExtractHour, ExtractWeekDay

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
        # Get course type filter from query parameters
        course_type = request.GET.get("courseType", "All")
        
        # Create base queryset with related data
        queryset = Attendance.objects.select_related("session__course__type")
        
        # Apply course type filter if needed
        if course_type != "All":
            queryset = queryset.filter(
                Q(session__course__type__typeName=course_type)
            )

        # Annotate with time and weekday information
        annotated = queryset.annotate(
            hour=ExtractHour('checked_date'),
            weekday=(ExtractWeekDay('checked_date') - 2) % 7  # Convert to Mon=0, Sun=6
        ).filter(hour__gte=9, hour__lte=17)  # Only include hours 9am-5pm

        # Aggregate data
        heatmap_data = (
            annotated.values('weekday', 'hour')
            .annotate(total=Count('id'))
            .order_by('weekday', 'hour')
        )

        # Create time slot mapping and day mapping
        time_mapping = {
            9: "9am",
            10: "10am",
            11: "11am",
            12: "12pm",
            13: "1pm",
            14: "2pm",
            15: "3pm",
            16: "4pm",
            17: "5pm"
        }
        
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        result = {day: {time: 0 for time in time_mapping.values()} for day in days}

        # Populate the result dictionary
        for entry in heatmap_data:
            day_index = entry['weekday']
            hour = entry['hour']
            count = entry['total']
            
            if 0 <= day_index < 7 and hour in time_mapping:
                day_name = days[day_index]
                time_slot = time_mapping[hour]
                result[day_name][time_slot] = count

        # Calculate percentages relative to maximum count
        max_count = max(
            entry['total'] for entry in heatmap_data
        ) if heatmap_data else 1  # Prevent division by zero

        # Convert counts to percentages
        for day in days:
            for time_slot in result[day]:
                if max_count > 0:
                    result[day][time_slot] = round((result[day][time_slot] / max_count) * 100, 2)

        return Response(result, status=status.HTTP_200_OK)

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
