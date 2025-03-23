from django.core.management.base import BaseCommand
from django.db import transaction
from api.models import User, Teacher, Student, Type, Course, CourseSession, Attendance, Storage, Receipt, Certificate
from api.management.commands.populate_db import populate_database  # Adjust import based on your script location

class Command(BaseCommand):
    help = "Clears and repopulates the database with sample data."

    def handle(self, *args, **kwargs):
        self.stdout.write("🗑️ Deleting all data...")

        with transaction.atomic():  # Ensure rollback safety
            Attendance.objects.all().delete()
            CourseSession.objects.all().delete()
            Student.objects.all().delete()
            Teacher.objects.all().delete()
            Course.objects.all().delete()
            Type.objects.all().delete()
            Storage.objects.all().delete()
            Receipt.objects.all().delete()
            Certificate.objects.all().delete()
            User.objects.exclude(is_superuser=True).delete()  # Keep superusers

        self.stdout.write("✅ Database cleared. Populating new data...")
        
        populate_database()

        self.stdout.write(self.style.SUCCESS("🎉 Database reset and repopulated!"))
