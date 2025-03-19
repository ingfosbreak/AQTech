import random
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from api.models import (
    User, Teacher, Student, Level, Course, CourseSession, 
    Attendance, Receipt, Certificate, Storage
)

User = get_user_model()  # Use custom User model if applicable

# ------------------------- Create Users -------------------------
def create_users():
    users = [
        {"username": "staff", "password": "admin123", "email": "staff@example.com", "role": "staff", "join_date": datetime.now()},
        {"username": "teacher1", "password": "pass123", "email": "teacher1@example.com", "role": "teacher", "join_date": datetime.now() - timedelta(days=100)},
        {"username": "teacher2", "password": "pass123", "email": "teacher2@example.com", "role": "teacher", "join_date": datetime.now() - timedelta(days=90)},
        {"username": "parent1", "password": "pass123", "email": "parent1@example.com", "role": "user", "join_date": datetime.now() - timedelta(days=50)},
        {"username": "parent2", "password": "pass123", "email": "parent2@example.com", "role": "user", "join_date": datetime.now() - timedelta(days=30)},
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
    level_objs = {name: Level.objects.get_or_create(levelName=name)[0] for name in levels}

    courses_data = [
        {"courseName": "Python Basics", "description": "Learn Python from scratch", "level": level_objs["Beginner"]},
        {"courseName": "Machine Learning", "description": "ML basics", "level": level_objs["Intermediate"]},
        {"courseName": "Django Web Development", "description": "Build web apps using Django", "level": level_objs["Advanced"]},
    ]

    course_objs = []
    for data in courses_data:
        course, created = Course.objects.update_or_create(
            courseName=data["courseName"],
            defaults={"description": data["description"], "level": data["level"], "created_at": now()},
        )
        course_objs.append(course)

    print(f"✅ Created {len(level_objs)} levels & {len(course_objs)} courses.")
    return course_objs


def create_teachers(users):
    teachers = [Teacher.objects.create(user=u, name=u.username) for u in users if u.role == "teacher"]
    
    if not teachers:
        print("⚠️ No teachers created! Check user roles.")

    print(f"✅ Created {len(teachers)} teachers.")
    return teachers



def create_students(users):
    students = [
        Student.objects.create(user=u, name=u.username)
        for u in users
        if u.role == "user"  # ✅ Since "students" are children of "users"
    ]

    print(f"✅ Created {len(students)} students.")
    return students

def create_course_sessions(courses, teachers, students):
    if not teachers:
        print("⚠️ No teachers available! Skipping session creation.")
        return []

    sessions = []

    for student in students:
        num_sessions = random.randint(1, 3)  # Each student gets 1 to 3 sessions
        for _ in range(num_sessions):
            session = CourseSession.objects.create(
                course=random.choice(courses),
                teacher=random.choice(teachers),  # ✅ Safe because teachers exist
                student=student,  
                session_date=datetime.now() + timedelta(days=random.randint(1, 30)),
                total_quota=1,
                start_time="10:00",
                end_time="12:00",
            )
            sessions.append(session)

    print(f"✅ Created {len(sessions)} unique course sessions.")
    return sessions


# ------------------------- Assign Students to Course Sessions -------------------------
def assign_students_to_sessions(students, sessions):
    for student in students:
        assigned_sessions = random.sample(sessions, k=random.randint(1, len(sessions)))
        student.sessions.set(assigned_sessions)  # Assign Many-to-Many sessions
        student.save()

    print(f"✅ Assigned students to sessions.")


# ------------------------- Create Attendance -------------------------
def create_attendance(sessions, teachers, students):
    attendance_objs = [
        Attendance.objects.create(
            session=random.choice(sessions),
            teacher=random.choice(teachers),
            student=random.choice(students),
            status="Present",
            attendance_date=datetime.now(),
            checked_date=datetime.now(),
            start_time="10:00",
            end_time="12:00",
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
    teachers = create_teachers(users)
    students = create_students(users)  # ✅ Create students first
    sessions = create_course_sessions(courses, teachers, students)  # ✅ Create unique sessions per student
    create_attendance(sessions, teachers, students)
    create_storage()
    create_receipts(students, sessions)
    create_certificates(users, courses)
    print("🎉 Database successfully populated!")


populate_database()
