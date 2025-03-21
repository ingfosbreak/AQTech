from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Avg
from api import models
from api.models import Student, Teacher, CourseSession
from django.utils.timezone import now
from datetime import timedelta
from datetime import time
from django.db.models import Q
from django.utils import timezone
from api.models.attendance import Attendance
from api.models import Attendance
from django.db.models.functions import TruncDate
from django.db.models.functions import ExtractHour, ExtractWeekDay, Extract
from django.db.models.functions import TruncMonth
from django.utils.timezone import make_naive

from api.models.course import Course

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
        courseType = request.GET.get('courseType', 'All')  # Default to 'All' if no courseType is specified
        
        if courseType != 'All':
            # Assuming Type model has a field named 'typeName'
            student_count = Student.objects.filter(sessions__course__type__typeName=courseType).distinct().count()
            teacher_count = Teacher.objects.filter(sessions__course__type__typeName=courseType).distinct().count()
        else:
            student_count = Student.objects.count()
            teacher_count = Teacher.objects.count()

        data = [
            {"name": "Student", "value": student_count},
            {"name": "Teacher", "value": teacher_count}
        ]

        return Response(data, status=status.HTTP_200_OK)

class AttendanceHeatmapView(APIView):
    def get(self, request):
        # Get course type filter from query parameters
        course_type = request.GET.get("courseType", "All")

        # Base queryset with necessary joins
        queryset = Attendance.objects.select_related("session__course__type").only("checked_date")

        # Apply course type filter if needed
        if course_type != "All":
            queryset = queryset.filter(session__course__type__typeName=course_type)

        # Convert QuerySet to a list of dictionaries
        attendance_data = list(queryset.values("checked_date"))

        # Define time slots
        time_mapping = {
            9: "9am", 10: "10am", 11: "11am", 12: "12pm",
            13: "1pm", 14: "2pm", 15: "3pm", 16: "4pm",
            17: "5pm", 18: "6pm", 19: "7pm", 20: "8pm",
            21: "9pm", 22: "10pm",
        }

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        result = {day: {time: 0 for time in time_mapping.values()} for day in days}

        # Process raw data
        for entry in attendance_data:
            checked_datetime = entry["checked_date"]  # Keep timezone-aware datetime

            # Extract hour and weekday
            hour = checked_datetime.hour
            weekday = checked_datetime.weekday()  # Monday = 0, Sunday = 6

            if hour in time_mapping and 0 <= weekday < 7:
                day_name = days[weekday]
                time_slot = time_mapping[hour]
                result[day_name][time_slot] += 1  # Increment count

        # Calculate percentages relative to maximum count
        max_count = max((count for day in result.values() for count in day.values()), default=1)

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
                "studentId": attendance.student.id,
                "course": attendance.session.course.courseName,
                "courseType": attendance.session.course.type.typeName,
                "timestamp": attendance.checked_date.strftime("%Y-%m-%d %H:%M:%S"),  # Updated field
            }
            for attendance in queryset
        ]

        return Response(records, status=status.HTTP_200_OK)

class RecentAttendanceView(APIView):
    def get(self, request):
        # Get studentId from query parameters
        student_id = request.GET.get("studentId")
        
        if not student_id:
            return Response(
                {"error": "Missing required parameter: studentId"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Fetch last three recent attendance records
        recent_attendance = (
            Attendance.objects
            .filter(student_id=student_id)  # Assuming student_id is correct
            .order_by("-checked_date")[:3]
        )

        # Serialize data
        records = []
        for record in recent_attendance:
            # Ensure checked_date is a datetime object and timezone aware
            checked_date = record.checked_date
            
            if checked_date is not None:
                
                # Serialize data
                records.append({
                    "timestamp": checked_date.strftime("%Y-%m-%d %H:%M:%S"),
                    "status": record.status
                })

                # Add relative time labels (e.g., Yesterday, 2 days ago)
                now = timezone.now()
                diff = now - checked_date

                if diff.days == 0:
                    records[-1]['relativeTime'] = "Today"
                elif diff.days == 1:
                    records[-1]['relativeTime'] = "Yesterday"
                else:
                    records[-1]['relativeTime'] = f"{diff.days} days ago"

        return Response(records, status=status.HTTP_200_OK)
    
class CoursePerformanceView(APIView):
    def get(self, request):
        courseType = request.GET.get('courseType', 'All')  # Default to 'All' if no courseType is specified

        # Course Data
        course_data = []
        if courseType != 'All':
            course_data = CourseSession.objects.filter(course__type__typeName=courseType).annotate(
                month=TruncMonth('session_date')
            ).values(
                'month'
            ).annotate(
                courses=Count('course'),
                attendance=Avg('total_quota'),
                capacity=Count('id')
            ).order_by('month')
        else:
            course_data = CourseSession.objects.annotate(
                month=TruncMonth('session_date')
            ).values(
                'month'
            ).annotate(
                courses=Count('course'),
                attendance=Avg('total_quota'),
                capacity=Count('id')
            ).order_by('month')

        # Transform course_data to match frontend's expected structure
        transformed_course_data = []
        for item in course_data:
            transformed_course_data.append({
                'month': item['month'].strftime('%Y-%m'),  # Format the date
                'courses': item['courses'],
                'attendance': item['attendance'],
                'capacity': item['capacity'],
            })

        # Course Popularity Data
        course_popularity_data = []
        if courseType != 'All':
            courses = Course.objects.filter(type__typeName=courseType)
            course_popularity_data = courses.annotate(students=Count('sessions')).values('courseName', 'quota', 'students', 'type__typeName')
        else:
            course_popularity_data = Course.objects.annotate(students=Count('sessions')).values('courseName', 'quota', 'students', 'type__typeName')

        # Transform course_popularity_data to match frontend's expected structure
        transformed_course_popularity_data = []
        for item in course_popularity_data:
            transformed_course_popularity_data.append({
                'name': item['courseName'],
                'popularity': item['quota'],  # Assuming 'quota' is used as popularity
                'students': item['students'],
                'type': item['type__typeName'],
            })

        return Response({
            'courseData': transformed_course_data,
        }, status=status.HTTP_200_OK)