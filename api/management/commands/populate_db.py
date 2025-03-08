import random
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from api.models import (
    User, Teacher, Student, Level, Course, CourseSession, 
    Attendance, Receipt, Certificate, Storage
)

User = get_user_model()  # Use custom User model if applicable

# ------------------------- Create Users -------------------------
def create_users():
    users = [
        {"username": "admin", "password": "admin123", "email": "admin@example.com", "role": "admin", "join_date": datetime.now()},
        {"username": "teacher1", "password": "pass123", "email": "teacher1@example.com", "role": "teacher", "join_date": datetime.now() - timedelta(days=100)},
        {"username": "teacher2", "password": "pass123", "email": "teacher2@example.com", "role": "teacher", "join_date": datetime.now() - timedelta(days=90)},
        {"username": "student1", "password": "pass123", "email": "student1@example.com", "role": "student", "join_date": datetime.now() - timedelta(days=50)},
        {"username": "student2", "password": "pass123", "email": "student2@example.com", "role": "student", "join_date": datetime.now() - timedelta(days=30)},
    ]

    user_objs = []
    for user in users:
        obj = User.objects.create_user(**user)
        user_objs.append(obj)

    print(f"✅ Created {len(user_objs)} users.")
    return user_objs


# ------------------------- Create Levels & Courses -------------------------
def create_levels_and_courses():
    levels = ["Beginner", "Intermediate", "Advanced"]
    level_objs = [Level.objects.create(levelName=l) for l in levels]

    courses = [
        {"courseName": "Python Basics", "description": "Learn Python from scratch", "level": level_objs[0]},
        {"courseName": "Machine Learning", "description": "ML basics", "level": level_objs[1]},
        {"courseName": "Django Web Development", "description": "Build web apps using Django", "level": level_objs[2]},
    ]
    course_objs = [Course.objects.create(**c) for c in courses]

    print(f"✅ Created {len(level_objs)} levels & {len(course_objs)} courses.")
    return course_objs


# ------------------------- Create Teachers & Students -------------------------
def create_teachers_and_students(users, courses):
    teachers = [Teacher.objects.create(user=u, name=u.username) for u in users if u.role == "teacher"]
    students = []

    for u in users:
        if u.role == "student":
            student = Student.objects.create(user=u, name=u.username)
            assigned_courses = random.sample(courses, k=random.randint(1, len(courses)))  # Assign random courses
            student.courses.set(assigned_courses)  # ManyToMany assignment
            students.append(student)

    print(f"✅ Created {len(teachers)} teachers & {len(students)} students (with courses).")
    return teachers, students


# ------------------------- Create Course Sessions -------------------------
def create_course_sessions(courses, teachers, students):
    sessions = []
    for i in range(1, 6):  # Create 5 sessions
        session = CourseSession.objects.create(
            course=random.choice(courses),
            teacher=random.choice(teachers),
            student=random.choice(students),
            session_date=datetime.now() + timedelta(days=i),
            total_quota=20,
            start_time="10:00",
            end_time="12:00",
        )
        sessions.append(session)

    print(f"✅ Created {len(sessions)} course sessions.")
    return sessions


# ------------------------- Create Attendance Records -------------------------
def create_attendance(sessions, teachers, students):
    attendance_objs = [
        Attendance.objects.create(
            session=random.choice(sessions),
            teacher=random.choice(teachers),
            student=random.choice(students),
            status="Present",
            attendance_date=datetime.now(),
            checked_date=datetime.now(),
        )
        for _ in range(5)
    ]

    print(f"✅ Created {len(attendance_objs)} attendance records.")
    return attendance_objs


# ------------------------- Create Storage Items -------------------------
def create_storage():
    storage_items = [
        {"title": "Laptop", "storage_image": None, "quantity": 5},
        {"title": "Projector", "storage_image": None, "quantity": 2},
    ]
    storage_objs = [Storage.objects.create(**s) for s in storage_items]

    print(f"✅ Created {len(storage_objs)} storage items.")
    return storage_objs


# ------------------------- Create Receipts -------------------------
def create_receipts(students, sessions):
    receipts = [
        Receipt.objects.create(
            student=random.choice(students),
            session=random.choice(sessions),
            amount=1000,
            payment_date=datetime.now(),
            payment_method="Credit Card",
            transaction_id=f"TXN{random.randint(1000,9999)}"
        )
        for _ in range(3)
    ]

    print(f"✅ Created {len(receipts)} receipts.")
    return receipts


# ------------------------- Create Certificates -------------------------
def create_certificates(users, courses):
    certificates = [
        Certificate.objects.create(
            user=random.choice(users),
            course=random.choice(courses),
            status="Completed"
        )
        for _ in range(2)
    ]

    print(f"✅ Created {len(certificates)} certificates.")
    return certificates


# ------------------------- Run All Functions -------------------------
def populate_database():
    users = create_users()
    courses = create_levels_and_courses()
    teachers, students = create_teachers_and_students(users, courses)
    sessions = create_course_sessions(courses, teachers, students)
    create_attendance(sessions, teachers, students)
    create_storage()
    create_receipts(students, sessions)
    create_certificates(users, courses)
    print("🎉 Database successfully populated!")


populate_database()
