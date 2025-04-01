import random
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from api.models import (
    User, Teacher, Student, Category, Course, CourseSession, 
    Attendance, Receipt, Certificate, Storage, Timeslot
)
from api.models.category import Category
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Populate the database with sample data'

    def handle(self, *args, **kwargs):
        populate_database()
        self.stdout.write("Database populated successfully!")

User = get_user_model()  # Use custom User model if applicable

# ------------------------- Create Users -------------------------
def create_users():
    users = [
        {"username": "staff", "password": "admin123", "email": "staff@example.com", "role": "staff", "join_date": timezone.now()},
        {"username": "teacher1", "password": "pass123", "email": "teacher1@example.com", "role": "teacher", "join_date": timezone.now() - timedelta(days=100), "contact": "1234567890"},
        {"username": "teacher2", "password": "pass123", "email": "teacher2@example.com", "role": "teacher", "join_date": timezone.now() - timedelta(days=90), "contact": "0987654321"},
        {"username": "parent1", "password": "pass123", "email": "parent1@example.com", "role": "user", "join_date": timezone.now() - timedelta(days=90), "contact": "1122334455"},
    ]

    # Adding 8 more teachers
    for i in range(3, 11):  # Start from teacher3 to teacher10
        users.append({
            "username": f"teacher{i}",
            "password": "pass123",
            "email": f"teacher{i}@example.com",
            "role": "teacher",
            "join_date": timezone.now() - timedelta(days=100 - i * 10),  # Stagger the join dates for variety
            "contact": f"555123456{i}",  # Example phone number format
        })

    # Generate 10 "user" role accounts
    for i in range(1, 11):
        users.append({
            "username": f"user{i}",
            "password": "userpass123",
            "email": f"user{i}@example.com",
            "role": "user",
            "join_date": timezone.now() - timedelta(days=i * 10),
            "contact": f"555123456{i}",  # Example phone number format
        })

    user_objs = []
    for user in users:
        obj, created = User.objects.update_or_create(
            username=user["username"],
            defaults={
                "email": user["email"],
                "role": user["role"],
                "join_date": user["join_date"],
                "contact": user.get("contact", ""),  # Default to an empty string if no contact is provided
            }
        )
        obj.set_password(user["password"])
        obj.save()
        user_objs.append(obj)

    print(f"✅ Created or updated {len(user_objs)} users.")
    return user_objs

# ------------------------- Create Category & Course -------------------------
def create_categories_and_courses():
    # Categories for the courses
    categories_data = ["AquaKids", "Playsound", "Other"]
    
    # Create categories and store their objects in a dictionary
    category_objs = {name: Category.objects.get_or_create(categoryName=name)[0] for name in categories_data}

    # Courses Data
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

    # Now we are creating the courses
    course_objs = []
    for category_name, courses in courses_data.items():
        category = category_objs[category_name]
        
        for course_name in courses:
            course, created = Course.objects.update_or_create(
                name=course_name,
                defaults={
                    "description": f"This is a {category_name} course.",
                    "type": "unrestricted",  # Default type set to 'unrestricted'
                    "min_age": 5,  # Example value, this can be adjusted
                    "max_age": 12,  # Example value, this can be adjusted
                    "quota": 10,  # Example value, this can be adjusted
                    "category": category,
                    "created_at": datetime.now(),
                    "price": 3500,  # Default price
                }
            )
            course_objs.append(course)

    print(f"✅ Created {len(category_objs)} Categories & {len(course_objs)} Courses.")
    return course_objs

# ------------------------- Create Teachers -------------------------
def create_teachers(users):
    # Ensure that we have categories to assign to the teachers
    categories = Category.objects.all()
    
    if not categories:
        print("⚠️ No categories found. Please create categories first.")
        return []
    
    # Create teachers
    teachers = []
    for u in users:
        if u.role == "teacher":
            # Assign a category to the teacher, for example, random or specific category
            # Here, we assign the first category as a default. You can modify this logic as per your needs
            category = categories.first()  # Example: You can modify this logic to assign categories dynamically

            teacher = Teacher.objects.create(
                user=u,
                name=u.username,
                category=category,  # Assign the category to the teacher
                status='active'  # Default status can be 'active'
            )
            teachers.append(teacher)
    
    if not teachers:
        print("⚠️ No teachers created! Check user roles.")

    print(f"✅ Created {len(teachers)} teachers.")
    return teachers


# ------------------------- Create Student -------------------------
def create_students(users):
    student_names = [
        "Alice", "Bob", "Charlie", "Daisy", "Ethan", "Fiona", "George", "Hannah",
        "Isaac", "Jack", "Katie", "Leo", "Mia", "Nathan", "Olivia", "Paul", "Quincy",
        "Rachel", "Sophia", "Tom", "Uma", "Victor", "Wendy", "Xander", "Yara", "Zane",
        "Amelia", "Ben", "Cathy", "David", "Ella", "Freddie", "Gina", "Henry", "Ivy",
        "James", "Kara", "Liam", "Megan", "Nina", "Oscar", "Penny", "Quinn", "Reuben",
        "Sarah", "Toby", "Ursula", "Vera", "Walter", "Xena", "Yasmine", "Zara"
    ]
    
    students = []
    name_index = 0  # To keep track of assigned names

    for u in users:
        if u.role == "user":
            num_students = 2 if name_index < 20 else 1  # Some users have 2 students
            for _ in range(num_students):
                if name_index >= len(student_names):  # Prevent index error if we run out of names
                    break
                # Create a student with a birthdate (e.g., set it to today or any date you prefer)
                birthdate = timezone.now().date()  # You can replace this with another logic for birthdate
                
                # Set all students' status to 'active'
                status = 'active'  # All students will have the 'active' status

                student = Student.objects.create(
                    user=u, 
                    name=student_names[name_index], 
                    birthdate=birthdate,
                    status=status  # Set the status here to 'active'
                )
                students.append(student)
                name_index += 1  # Move to the next name

    print(f"✅ Created {len(students)} students.")
    return students

# ------------------------- Create Session -------------------------
def create_sessions(courses, teachers, students):
    if not teachers:
        print("⚠️ No teachers available! Skipping session creation.")
        return []

    sessions = []

    for student in students:
        num_sessions = random.randint(1, 3)  # Each student gets 1 to 3 sessions
        for i in range(num_sessions):
            # Generate a name for the session
            session_name = f"{student.name}'s {random.choice(courses).name} Session {i+1}"

            # Create the session
            session = CourseSession.objects.create(
                course=random.choice(courses),  # Random course
                student=student,  # The current student
                name=session_name,  # The generated session name
                total_quota=1,  # Example quota (can be adjusted as needed)
            )
            sessions.append(session)

    print(f"✅ Created {len(sessions)} unique course sessions.")
    return sessions


# ------------------------- Assign Students to Course Sessions -------------------------
def assign_students_to_sessions(students, sessions):
    for student in students:
        # Pick a random number of sessions (at least 1, at most the total number of sessions)
        assigned_sessions = random.sample(sessions, k=random.randint(1, len(sessions)))

        # Assign each session to the student
        for session in assigned_sessions:
            session.student = student  # Assign the student to the session
            session.save()

    print(f"✅ Assigned students to sessions.")


# ------------------------- Create TimeSlot -------------------------
def create_timeslot(courses, num_timeslots=10):
    """Create a list of timeslots for multiple courses, scheduling weekly in the future."""
    timeslots = [
        '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00'
    ]
    
    # Start scheduling from next Monday
    today = datetime.today()
    days_until_monday = (7 - today.weekday()) % 7  # 0 if Monday, otherwise days until next Monday
    first_timeslot_date = today + timedelta(days=days_until_monday)

    for course in courses:
        for i in range(num_timeslots):
            start_time_str = random.choice(timeslots)
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            
            # Example end time (assuming 1-hour sessions)
            end_time = (datetime.combine(datetime.today(), start_time) + timedelta(hours=1)).time()
            
            # Calculate timeslot_date (weekly increment)
            timeslot_date = first_timeslot_date + timedelta(weeks=i)
            
            # Create the timeslot object
            Timeslot.objects.create(
                course=course,
                timeslot_date=timeslot_date,
                start_time=start_time,
                end_time=end_time
            )
        
        print(f"✅ {num_timeslots} timeslots created for course {course.name}.")

# ------------------------- Create Attendance -------------------------

# Function to generate a random time between 10 AM and 5 PM
def random_time():
    start_time = datetime.strptime("10:00", "%H:%M")
    end_time = datetime.strptime("17:00", "%H:%M")
    
    random_minutes = random.randint(0, int((end_time - start_time).total_seconds() / 60))
    random_datetime = start_time + timedelta(minutes=random_minutes)
    
    return random_datetime.strftime("%H:%M")


def create_attendance(sessions, teachers, students, timeslots):
    attendance_objs = []

    # Ensure timeslots is not empty
    if not timeslots:
        print("⚠️ Warning: No timeslots available. Skipping attendance creation.")
        return attendance_objs

    # Ensure timeslots contain valid instances
    valid_timeslots = Timeslot.objects.filter(id__in=[t.id for t in timeslots])

    if not valid_timeslots.exists():
        print("⚠️ Warning: No valid Timeslot instances found in the database.")
        return attendance_objs

    for _ in range(20):  # Create at least 20 attendance records
        session = random.choice(sessions)
        teacher = random.choice(teachers)
        student = random.choice(students)

        # Select a valid timeslot from the database
        timeslot = random.choice(valid_timeslots)

        # Randomly assign checked_date to a time between 10 AM and 5 PM
        checked_time_str = random_time()
        checked_date = timezone.now().replace(
            hour=int(checked_time_str.split(":")[0]),
            minute=int(checked_time_str.split(":")[1]),
            second=0,
            microsecond=0
        )

        # Create Attendance record
        attendance = Attendance.objects.create(
            session=session,
            teacher=teacher,
            student=student,
            timeslot=timeslot,  # Pass the Timeslot instance
            status=random.choice(["present", "absent"]),  # Randomize attendance status
            attendance_date=timezone.now().date(),
            start_time="11:00",  # Default start_time
            end_time="12:00",    # Default end_time
            checked_date=checked_date,
        )

        attendance_objs.append(attendance)

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
    courses = create_categories_and_courses()
    teachers = create_teachers(users)
    students = create_students(users)  # ✅ Create students first
    sessions = create_sessions(courses, teachers, students)  # ✅ Create unique sessions per student
    assign_students_to_sessions(students, sessions)
    timeslots = create_timeslot(courses)

    # Now pass the timeslots to the create_attendance function
    create_attendance(sessions, teachers, students, timeslots)

    print("🎉 Database successfully populated!")

