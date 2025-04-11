import random
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from api.models import (
    User, Teacher, Student, Category, Course, CourseSession, 
    Attendance, Receipt, Certificate, Storage, Timeslot, TeacherAssignment
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
    # Sample real names for teachers and users (you can add more names or get from an external source)
    teacher_names = [
        "John Smith", "Jane Doe", "James Brown", "Emily Davis", "Michael Wilson",
        "Sarah Lee", "David Harris", "Sophia Clark", "Daniel Lewis", "Megan Walker"
    ]
    user_names = [
        "Alice Johnson", "Bob Martin", "Charlie Evans", "Diana Walker", "Ethan Moore",
        "Grace Scott", "Hannah Baker", "Ian Adams", "Jack Taylor", "Kylie Carter"
    ]
    
    # Initialize users data
    users = [
        {"username": "staff", "password": "admin123", "email": "staff@example.com", "role": "staff", "join_date": timezone.now(), "first_name": "Staff", "last_name": "Member"},
    ]

    # Adding 8 teachers with real names
    for i in range(3, 11):  # Start from teacher3 to teacher10
        teacher_name = random.choice(teacher_names)  # Randomly pick a teacher's name
        teacher_names.remove(teacher_name)  # Remove the name to ensure no duplicates
        first_name, last_name = teacher_name.split()  # Split the name into first and last name
        users.append({
            "username": f"teacher{i}",
            "password": "pass123",
            "email": f"teacher{i}@example.com",
            "role": "teacher",
            "join_date": timezone.now() - timedelta(days=100 - i * 10),  # Stagger the join dates for variety
            "contact": f"555123456{i}",
            "first_name": first_name,
            "last_name": last_name,  # Assign first and last names
        })

    # Generate 10 "user" role accounts with real names
    for i in range(1, 11):
        user_name = random.choice(user_names)  # Randomly pick a user name
        user_names.remove(user_name)  # Remove the name to ensure no duplicates
        first_name, last_name = user_name.split()  # Split the name into first and last name
        users.append({
            "username": f"user{i}",
            "password": "userpass123",
            "email": f"user{i}@example.com",
            "role": "user",
            "join_date": timezone.now() - timedelta(days=i * 10),
            "contact": f"555123456{i}",
            "first_name": first_name,
            "last_name": last_name,  # Assign first and last names
        })

    user_objs = []
    for user in users:
        # Ensure that first_name and last_name are present
        first_name = user.get("first_name", "")
        last_name = user.get("last_name", "")
        
        # Update or create the user object
        obj, created = User.objects.update_or_create(
            username=user["username"],
            defaults={
                "email": user["email"],
                "role": user["role"],
                "join_date": user["join_date"],
                "contact": user.get("contact", ""),  # Default to an empty string if no contact is provided
                "first_name": first_name,  # Assign first_name
                "last_name": last_name,  # Assign last_name
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
def create_sessions(courses, students):

    sessions = []
    course_count = len(courses)

    # Loop through every student in the database and assign them to a course
    for index, student in enumerate(students):
        # Assign each student a course session in a round-robin manner
        course = courses[index % course_count]  # This ensures courses loop back once we run out

        # Generate the session name
        session_name = f"{student.name}'s {course.name} Session"

        # Create the session for the student
        session = CourseSession.objects.create(
            course=course,  # The selected course for the student
            student=student,  # The current student
            name=session_name,  # The generated session name
            total_quota=10,  # Example quota (can be adjusted as needed)
        )
        sessions.append(session)

    print(f"✅ Created {len(sessions)} course sessions for students.")
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
    """Create a list of timeslots for multiple courses, scheduling weekly in the future without collisions."""
    available_times = [
        '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00'
    ]
    
    # Start scheduling from next Monday
    today = datetime.today()
    days_until_monday = (7 - today.weekday()) % 7
    first_timeslot_date = today + timedelta(days=days_until_monday)

    for course in courses:
        used_times_per_date = {}  # Key: date, Value: list of used start times

        for i in range(num_timeslots):
            timeslot_date = first_timeslot_date + timedelta(weeks=i)

            # Get list of already used times for this date
            used_times = used_times_per_date.get(timeslot_date, [])

            # Find available times for this date
            remaining_times = [t for t in available_times if t not in used_times]
            if not remaining_times:
                print(f"⚠️ No more available timeslots on {timeslot_date} for course {course.name}.")
                continue

            # Pick a time randomly from remaining options
            start_time_str = random.choice(remaining_times)
            used_times.append(start_time_str)  # Mark it as used
            used_times_per_date[timeslot_date] = used_times

            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = (datetime.combine(datetime.today(), start_time) + timedelta(hours=1)).time()

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

    timeslots = Timeslot.objects.all()
    print(f"Debug: Found {timeslots.count()} timeslots")

    # Ensure timeslots is not empty
    if not timeslots:
        print("⚠️ Warning: No timeslots available. Skipping attendance creation.")
        return attendance_objs

    # Ensure timeslots contain valid instances
    valid_timeslots = Timeslot.objects.filter(id__in=[t.id for t in timeslots])

    if not valid_timeslots.exists():
        print("⚠️ Warning: No valid Timeslot instances found in the database.")
        return attendance_objs

    # Increase number of records to create (e.g., 50 records)
    for _ in range(50):  # Create at least 50 attendance records
        session = random.choice(sessions)
        teacher = random.choice(teachers)
        student = random.choice(students)

        # Select a valid timeslot from the database
        timeslot = random.choice(valid_timeslots)

        # Randomize the checked_time within today (not further off than the current time)
        checked_date = timezone.now()

        # Randomize time between 10:00 AM and current time (not in the future)
        hour = random.randint(10, checked_date.hour)  # Random hour between 10 AM and the current hour
        minute = random.randint(0, 59)  # Random minute within that hour
        checked_date = checked_date.replace(hour=hour, minute=minute, second=0, microsecond=0)

        if checked_date > timezone.now():  # Ensure the time is not in the future
            checked_date = timezone.now()

        # Randomize start_time and end_time within today's range
        start_hour = random.randint(10, checked_date.hour)  # Random start time between 10 AM and the current hour
        start_minute = random.randint(0, 59)
        start_time = checked_date.replace(hour=start_hour, minute=start_minute)

        # Ensure end_time is later than start_time, randomize duration between 30 minutes and 2 hours
        duration = random.randint(30, 120)  # Duration in minutes
        end_time = start_time + timedelta(minutes=duration)

        # Ensure end_time is not beyond the current time
        if end_time > timezone.now():
            end_time = timezone.now()

        # Create Attendance record
        attendance = Attendance.objects.create(
            session=session,
            teacher=teacher,
            student=student,
            timeslot=timeslot,  # Pass the Timeslot instance
            status=random.choice(["present", "absent"]),  # Randomize attendance status
            attendance_date=timezone.now().date(),
            start_time=start_time.strftime("%H:%M"),  # Format start_time as HH:MM
            end_time=end_time.strftime("%H:%M"),      # Format end_time as HH:MM
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
    receipts = []
    
    for _ in range(3):  # Create 3 receipts for example
        student = random.choice(students)  # Randomly pick a student
        session = random.choice(sessions)  # Randomly pick a session
        amount = session.course.price if hasattr(session, 'course') else 1000  # Use the course price if available, default to 1000
        
        receipt = Receipt.objects.create(
            student=student,
            session=session,
            amount=amount,
            payment_method="CARD",  # Assuming "CARD" for now; could be dynamic if needed
            receipt_number=f"INV-{timezone.now().year}-{random.randint(10000, 99999)}",  # Example receipt number
            notes=f"Payment for {session.course.name} registration",  # Example note based on course name
            items=[{"description": "Course Registration Fee", "amount": amount}]  # Example item
        )
        
        receipts.append(receipt)
    
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

def create_teacher_assignments():
    """Create TeacherAssignment records by assigning teachers to courses with matching categories."""
    courses = list(Course.objects.all())

    if not courses:
        print("No courses available to assign.")
        return

    assignments = []
    
    for course in courses:
        # Get teachers from the same category as the course
        eligible_teachers = list(Teacher.objects.filter(category=course.category))
        
        if not eligible_teachers:
            print(f"No teachers available for course: {course.name} (Category: {course.category})")
            continue
        
        teacher = random.choice(eligible_teachers)  # Assign a random eligible teacher
        assignments.append(TeacherAssignment(course=course, teacher=teacher))

    if assignments:
        TeacherAssignment.objects.bulk_create(assignments)
        print(f"Created {len(assignments)} teacher assignments.")
    else:
        print("No valid teacher assignments could be made.")

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
    sessions = create_sessions(courses, students)  # ✅ Create unique sessions per student
    assign_students_to_sessions(students, sessions)
    timeslots = create_timeslot(courses)
    create_teacher_assignments()
    create_receipts(students, sessions)
    # Now pass the timeslots to the create_attendance function
    create_attendance(sessions, teachers, students, timeslots)

    print("🎉 Database successfully populated!")

