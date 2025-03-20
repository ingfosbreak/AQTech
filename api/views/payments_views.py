import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from django.db import transaction
from api.models import CourseSession, Attendance, Course, Student
from django.http import JsonResponse
from django.utils import timezone
import urllib.parse

stripe.api_key = settings.STRIPE_SECRET_KEY

class CreatePaymentIntentView(APIView):
    def post(self, request):
        try:
            data = request.data
            amount = data.get("amount")  # Amount in cents
            currency = data.get("currency", "thb")  # Default to THB
            date = timezone.datetime.strptime(data.get("date"), "%Y-%m-%dT%H:%M:%S.%fZ").date()
            metadata = {
                "student_id": data.get("student_id"),  # Store student ID
                "course_id": data.get("course_id"),  # Store purchased course
                "teacher_id": data.get("teacher_id"),
                "date": date,
                "start_time": data.get("start_time"),
            }

            # Create PaymentIntent
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                payment_method_configuration="pmc_1R1AzmDCJUREqBVa83HoBBaA",
                metadata=metadata,
            )
            # receipt_email="aquacube2626@gmail.com" not working in test payment
            return Response({"client_secret": intent.client_secret}, status=status.HTTP_200_OK)

        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookAPIView(APIView):
    def post(self, request):
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError as e:
            print(e)
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            print(e)
            return HttpResponse(status=400)
        
        if event["type"] == "payment_intent.succeeded":
            payment_intent = event["data"]["object"]
            metadata = payment_intent.get("metadata", {})  # Get metadata from Stripe session         
            

            # receipt is not working in testmode
            success = create_course_session_and_attendance(metadata)
            if success:
                return JsonResponse({"message": "Created CourseSession and Attendance Success"}, status=status.HTTP_201_CREATED)
            else:
                return JsonResponse({"message": "Failed to create CourseSession or Attendance"}, status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse({"message": "Event type not handled"}, status=status.HTTP_400_BAD_REQUEST)


def create_course_session_and_attendance(metadata):
    try:
        with transaction.atomic():  # Ensures atomicity of the operations
            # Prepare CourseSession data
            teacher_id = metadata.get('teacher_id')
            student_id = metadata.get('student_id')
            course_id = metadata.get('course_id')
            session_date_str = metadata.get('date')
            start_time_str = metadata.get('start_time')

            session_date = timezone.datetime.strptime(session_date_str, "%Y-%m-%d").date()
            start_time = datetime.strptime(start_time_str, "%I:%M %p").time()

            start_datetime = datetime.combine(session_date, start_time)
            end_datetime = start_datetime + timedelta(hours=1)  # End time is 1 hour after start_time
            end_time = end_datetime.time()

            try:
                course = Course.objects.get(id=course_id)
            except Course.DoesNotExist:
                return False  
            
            total_quota = course.quota

            course_session = CourseSession.objects.create(
                teacher_id=teacher_id,
                student_id=student_id,
                course_id=course_id,
                session_date=session_date,
                start_time=start_time,
                end_time=end_time,
                total_quota=total_quota,
            )

            if not course_session:
                return False

            # Prepare Attendance data
            teacher = course_session.teacher
            student = course_session.student
            session_date = course_session.session_date

            # Create attendance records for 10 weeks (adjust as needed)
            attendance_data = [
                Attendance(
                    session=course_session,
                    teacher=teacher,
                    student=student,
                    attendance_date=course_session.session_date + timedelta(weeks=i),
                    status="absent",  # Default status
                    end_time=end_time,
                    start_time=start_time,
                )
                for i in range(course_session.total_quota)
            ]

            # Bulk create attendance records
            Attendance.objects.bulk_create(attendance_data)

            return True  # Everything was successful, return True

    except Exception as e:
        print(f"Error creating course session or attendance: {e}")
        return False  # In case of any exception, return False

class HandleBeforePaymentView(APIView):
    def post(self, request):
        student_id = request.data.get("student_id")
        course_id = request.data.get("course_id")
        date_str = request.data.get("date")
        start_time_str = request.data.get('start_time')

        if not student_id:
            return JsonResponse({"error": "Missing required parameters."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = Student.objects.get(id=student_id)
        except (Student.DoesNotExist):
            return JsonResponse({"error": "student not found."}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            course = Course.objects.get(id=course_id)
        except:
            return JsonResponse({"error": "course not found."}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            decoded_date_str = urllib.parse.unquote(date_str)
            date_obj = timezone.datetime.strptime(decoded_date_str, "%Y-%m-%dT%H:%M:%S.%fZ").date()
            start_time = datetime.strptime(start_time_str, "%I:%M %p").time()  # Parse start time
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        today = timezone.localtime().date()
        now = timezone.localtime()
        start_datetime = datetime.combine(date_obj, start_time)
        start_datetime = timezone.make_aware(start_datetime, timezone.get_current_timezone())
        end_datetime = start_datetime + timedelta(hours=1)
        end_time = end_datetime.time()

        if date_obj < today:
            return JsonResponse({"error": "The date must be today or in the future."}, status=status.HTTP_400_BAD_REQUEST)
        
        if date_obj == today:
            if start_datetime <= now:
                return JsonResponse({"error": "The start time must be in the future."}, status=status.HTTP_400_BAD_REQUEST)
        

        attendance_data = []
        for i in range(course.quota):
            check_date = date_obj + timedelta(weeks=i)

            if Attendance.objects.filter(
                student=student,
                attendance_date=check_date,
                start_time=start_time
            ).exists():
                return JsonResponse(
                    {"error": f"Student already has a class on {check_date} at {start_time}."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                attendance_data.append({
                    "id": 0,  # You can set it to None since you're not saving it to the database
                    "status": "Absent",  # Or any status that fits your use case
                    "session_id": None,  # No session ID if it's not actually created
                    "session_date": check_date,  # Set the check_date for session date
                    "course_id": course.id,  # Course ID
                    "course_name": course.courseName,  # You can replace `course.name` with the appropriate field
                    "teacher_id": None,  # Teacher ID, leave None if not actually creating
                    "teacher_name": "System",  # Placeholder for teacher name
                    "student_id": student.id,  # Student ID
                    "student_name": f"{student.name}",
                    "attendance_date": check_date,  # Attendance date (same as session date)
                    "start_time": start_time,  # Start time from your logic
                    "end_time": end_time,  # End time (you need to set `end_time` appropriately)
                    "is_owner": student.id == int(student_id),  # Check if the student is the owner
                })
                
        return JsonResponse(attendance_data, safe=False, status=status.HTTP_200_OK)