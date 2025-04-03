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
from django.utils.timezone import localtime
from django.core.exceptions import ObjectDoesNotExist

from api.models.category import Category
from api.models.course import Course

class CombinedCountView(APIView):
    def get(self, request):
        # Total number of students
        total_student = Student.objects.count()

        # Active students (students who have at least one course session)
        active_student = Student.objects.filter(
            sessions__isnull=False  # Check if the student has any related CourseSession
        ).distinct().count()

        # Inactive students (students who have no course session)
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
        # Get the category parameter from the GET request, default to 'All' if not provided
        category_name = request.GET.get('category', 'All')

        # Handle 'All' case, no filtering
        if category_name == 'All':
            student_count = Student.objects.count()
            teacher_count = Teacher.objects.count()
        else:
            try:
                # Try to get the category object by categoryName
                category = Category.objects.get(categoryName=category_name)

                # Filter students based on the course's category
                student_count = Student.objects.filter(sessions__course__category=category).distinct().count()

                # Filter teachers based on their category
                teacher_count = Teacher.objects.filter(category=category).count()

            except Category.DoesNotExist:
                # If the category does not exist, return an error response
                return Response({"error": "Category not found"}, status=400)

        # Prepare the response data
        data = [
            {"name": "Student", "value": student_count},
            {"name": "Teacher", "value": teacher_count}
        ]

        # Return the data as a JSON response
        return Response(data)

    
class AttendanceHeatmapView(APIView):
    def get(self, request):
        # Get course type filter from query parameters
        course_type = request.GET.get("courseType", "All")

        # Create base queryset with related data, excluding null checked_date
        queryset = Attendance.objects.select_related("session__course__type").exclude(checked_date__isnull=True)

        # Apply course type filter if needed
        if course_type != "All":
            queryset = queryset.filter(Q(session__course__type__typeName=course_type))

        # Extract hour and weekday with local time conversion
        heatmap_data = []
        for attendance in queryset:
            if attendance.checked_date:  # Ensure checked_date is not None
                local_checked_date = localtime(attendance.checked_date)  # Convert to local timezone
                hour = local_checked_date.hour
                weekday = local_checked_date.weekday()  # Monday = 0, Sunday = 6

                heatmap_data.append({"weekday": weekday, "hour": hour})

        # Create time slot mapping and day mapping
        time_mapping = {
            9: "9am", 10: "10am", 11: "11am", 12: "12pm", 13: "1pm",
            14: "2pm", 15: "3pm", 16: "4pm", 17: "5pm", 18: "6pm",
            19: "7pm", 20: "8pm", 21: "9pm", 22: "10pm",
        }

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        result = {day: {time: 0 for time in time_mapping.values()} for day in days}

        # Count occurrences
        for entry in heatmap_data:
            day_index = entry["weekday"]
            hour = entry["hour"]

            if 0 <= day_index < 7 and hour in time_mapping:
                day_name = days[day_index]
                time_slot = time_mapping[hour]
                result[day_name][time_slot] += 1  # Increment count

        # Return the raw count values, no need to convert to percentages
        return Response(result, status=status.HTTP_200_OK)

class AttendanceLogView(APIView):
    def get(self, request):
        search_term = request.GET.get("search", "").strip().lower()
        sort_newest_first = request.GET.get("sortNewestFirst", "true").lower() == "true"

        # Exclude records with null checked_date
        queryset = Attendance.objects.select_related(
            "student", "teacher", "timeslot"
        ).exclude(checked_date__isnull=True)

        # Apply search filter
        if search_term:
            queryset = queryset.filter(
                Q(student__name__icontains=search_term) |
                Q(session__course__name__icontains=search_term) |
                Q(checked_date__icontains=search_term)  # Updated to checked_date, if it still makes sense
            )

        # Apply sorting
        queryset = queryset.order_by("-checked_date" if sort_newest_first else "checked_date")

        # Serialize data
        records = [
            {
                "id": attendance.id,
                "name": attendance.student.name,
                "studentId": attendance.student.id,
                "course": attendance.session.course.name,
                "category": attendance.session.course.category.categoryName,  # Added categoryName
                "attendanceDate": attendance.attendance_date.strftime("%Y-%m-%d"),  # Directly use attendance_date
                "startTime": attendance.start_time.strftime("%H:%M:%S") if attendance.start_time else None,  # No localtime for TimeField
                "endTime": attendance.end_time.strftime("%H:%M:%S") if attendance.end_time else None,  # No localtime for TimeField
                "teacherName": attendance.teacher.name,
                "timeslot": attendance.timeslot.id,  # Assuming the timeslot can be identified by ID or another field
                "timestamp": localtime(attendance.checked_date).strftime("%Y-%m-%d %H:%M:%S"),
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