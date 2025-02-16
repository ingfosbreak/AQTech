from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import User, Student, Teacher, Level, Course, CourseSession, Attendance, Certificate, Receipt

class Command(BaseCommand):
    help = 'Populate the database with sample data'

    def handle(self, *args, **kwargs):
        # Create Users
        user1 = User.objects.create_user(username='student1', password='password', role='user')
        user2 = User.objects.create_user(username='teacher1', password='password', role='teacher')

        # Create Students
        student1 = Student.objects.create(user=user1, name='John Doe', dob='2000-01-01', contact='1234567890', email='john@example.com')

        # Create Teachers
        teacher1 = Teacher.objects.create(user=user2, name='Jane Smith')

        # Create Levels
        level1 = Level.objects.create(levelName='Beginner')
        level2 = Level.objects.create(levelName='Intermediate')

        # Create Courses
        course1 = Course.objects.create(courseName='Python Basics', description='Introduction to Python programming.', level=level1)
        course2 = Course.objects.create(courseName='Advanced Python', description='Deep dive into Python programming.', level=level2)

        # Create Course Sessions
        session1 = CourseSession.objects.create(course=course1, teacher=teacher1, student=student1,
                                                 session_number=1, session_date=timezone.now().date(),
                                                 total_quota=10, start_time=timezone.now().time(), 
                                                 end_time=(timezone.now() + timezone.timedelta(hours=1)).time())

        # Create Attendance Records
        Attendance.objects.create(student=student1, session=session1, teacher=teacher1,
                                  status='present', attendance_date=timezone.now(), checked_date=timezone.now())

        # Create Certificates
        Certificate.objects.create(user=user1, course=course1,
                                    status='issued')

        # Create Receipts
        Receipt.objects.create(student=student1, session=session1,
                                amount=100.00, payment_method='Credit Card',
                                transaction_id='TRANS123456')

        self.stdout.write(self.style.SUCCESS('Database populated successfully!'))
