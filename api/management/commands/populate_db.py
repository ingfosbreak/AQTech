import random
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from api.models import (
    User, Teacher, Student, Type, Course, CourseSession, 
    Attendance, Receipt, Certificate, Storage
)

User = get_user_model()  # Use custom User model if applicable

# ------------------------- Create Users -------------------------
def create_users():
    users = [
        {"username": "staff", "password": "admin123", "email": "staff@example.com", "role": "staff", "join_date": timezone.now()},
        {"username": "teacher1", "password": "pass123", "email": "teacher1@example.com", "role": "teacher", "join_date": timezone.now() - timedelta(days=100)},
        {"username": "teacher2", "password": "pass123", "email": "teacher2@example.com", "role": "teacher", "join_date": timezone.now() - timedelta(days=90)},
        {"username": "parent1", "password": "pass123", "email": "parent1@example.com", "role": "user", "join_date": timezone.now() - timedelta(days=90)},
    ]

    # Generate 10 "user" role accounts
    for i in range(1, 11):
        users.append({
            "username": f"user{i}",
            "password": "userpass123",
            "email": f"user{i}@example.com",
            "role": "user",
            "join_date": timezone.now() - timedelta(days=i * 10),
        })

    user_objs = []
    for user in users:
        obj, created = User.objects.update_or_create(
            username=user["username"],
            defaults={
                "email": user["email"],
                "role": user["role"],
                "date_joined": user["join_date"],
            }
        )
        obj.set_password(user["password"])
        obj.save()
        user_objs.append(obj)

    print(f"✅ Created or updated {len(user_objs)} users.")
    return user_objs



def create_types_and_courses():
    types = ["AquaKids", "Playsound", "Other"]
    type_objs = {name: Type.objects.get_or_create(typeName=name)[0] for name in types}
    
    courses_data = {
        "AquaKids": [
            "Swimming Baby Class",
            "Advanced Aqua Training",
            "Junior Water Polo",
            "Aqua Aerobics for Kids",
            "Deep Dive Basics",
            "Underwater Exploration",
            "Freestyle Fundamentals",
            "Backstroke Basics",
            "Synchronized Swimming",
            "Water Safety Training",
        ],
        "Playsound": [
            "Beginning to Be Pianist",
            "Guitar for Beginners",
            "Violin Mastery",
            "Drumming Essentials",
            "Music Theory Basics",
            "Jazz Improvisation",
            "Orchestra Training",
            "Songwriting Workshop",
            "Electronic Music Production",
            "Choral Singing",
        ],
        "Other": [
            "Taekwondo Class",
            "Play Dough Class",
            "Beginner Ballet",
            "Creative Painting",
            "Drama & Acting",
            "Chess Strategy",
            "Robotics Workshop",
            "Coding for Kids",
            "Lego Engineering",
            "Public Speaking",
        ],
    }
    
    course_objs = []
    for type_name, courses in courses_data.items():
        for course_name in courses:
            course, created = Course.objects.update_or_create(
                courseName=course_name,
                defaults={"description": f"This is a {type_name} course.", "type": type_objs[type_name], "created_at": now(), "price": 3500},
            )
            course_objs.append(course)
    
    print(f"✅ Created {len(type_objs)} Types & {len(course_objs)} Courses.")
    return course_objs

def create_teachers(users):
    teachers = [Teacher.objects.create(user=u, name=u.username) for u in users if u.role == "teacher"]
    
    if not teachers:
        print("⚠️ No teachers created! Check user roles.")

    print(f"✅ Created {len(teachers)} teachers.")
    return teachers


def create_students(users):
    student_names = [
        "Alice", "Bob", "Charlie", "Daisy", "Ethan", "Fiona", "George", "Hannah",
        "Isaac", "Jack", "Katie", "Leo", "Mia", "Nathan"
    ]
    
    students = []
    name_index = 0  # To keep track of assigned names

    for u in users:
        if u.role == "user":
            num_students = 2 if name_index < 10 else 1  # Some users have 2 students
            for _ in range(num_students):
                if name_index >= len(student_names):  # Prevent index error
                    break
                student = Student.objects.create(user=u, name=student_names[name_index])
                students.append(student)
                name_index += 1  # Move to the next name

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
                session_date=timezone.now() + timedelta(days=random.randint(1, 30)),
                total_quota=1,
                start_time="11:00",
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

# Function to generate a random time between 10 AM and 5 PM
def random_time():
    start_time = datetime.strptime("10:00", "%H:%M")
    end_time = datetime.strptime("17:00", "%H:%M")
    
    # Generate a random time within this range
    random_minutes = random.randint(0, int((end_time - start_time).total_seconds() / 60))
    random_datetime = start_time + timedelta(minutes=random_minutes)
    
    return random_datetime.strftime("%H:%M")

def create_attendance(sessions, teachers, students):
    # Create Attendance records with random checked_date and times
    attendance_objs = [
        Attendance.objects.create(
            session=random.choice(sessions),
            teacher=random.choice(teachers),
            student=random.choice(students),
            status="absent",
            attendance_date=timezone.now(),
            # Randomly assign checked_date to a time between 10 AM and 5 PM
            checked_date=timezone.now().replace(hour=int(random_time().split(":")[0]), minute=int(random_time().split(":")[1]), second=0, microsecond=0),
            start_time="11:00",
            end_time="12:00",
        )
        for _ in range(20)  # Create at least 20 records
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
            payment_date=timezone.now(),
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
def is_database_populated():
    return (
        User.objects.exists() and
        Course.objects.exists() and
        Teacher.objects.exists() and
        Student.objects.exists() and
        CourseSession.objects.exists()
    )

def populate_database():
    if is_database_populated():
        print("✅ Database is already populated. Skipping population.")
        return
    
    users = create_users()
    courses = create_types_and_courses()
    teachers = create_teachers(users)
    students = create_students(users)  # ✅ Create students first
    sessions = create_course_sessions(courses, teachers, students)  # ✅ Create unique sessions per student
    create_attendance(sessions, teachers, students)
    create_storage()
    # create_receipts(students, sessions)
    # create_certificates(users, courses)
    print("🎉 Database successfully populated!")

