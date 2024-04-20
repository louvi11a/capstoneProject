import sys
from django.utils import timezone
from orphans.models import Subject, Education, Grade, Info
import os
import django
from faker import Faker
from random import randint, choice
# Adjust this path to the root of your Django project
sys.path.append(
    'c:/Users/Louvilla/myProjects/capstoneProject/orphanage_system')
# Replace 'capstone.settings' with your actual settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orphanage_system.settings')
django.setup()

django.setup()


fake = Faker()


def create_subjects():
    subjects = ['Mathematics', 'Science', 'History',
                'English', 'Art', 'Music', 'Physical Education']
    for name in subjects:
        Subject.objects.get_or_create(name=name)


def create_education(num, orphans):
    create_subjects()  # Ensure subjects exist before assigning
    for _ in range(num):
        # Assuming you have some orphans in your database
        orphan = choice(orphans)
        education_level = choice(['Elementary', 'High School', 'College'])
        school_name = fake.company()
        year_level = randint(1, 12) if education_level != 'College' else None
        # GPA between 2.00 and 4.00
        current_gpa = round(randint(200, 400) / 100.0, 2)

        education = Education.objects.create(
            orphan=orphan,
            education_level=education_level,
            school_name=school_name,
            year_level=year_level,
            current_gpa=current_gpa,
            date_recorded=timezone.now().date()
        )
        create_grades(education)


def create_grades(education):
    subjects = Subject.objects.all()
    for subject in subjects:
        for semester in range(1, 3):  # Assuming two semesters
            for quarter in range(1, 5):  # Assuming four quarters
                grade_value = choice(
                    [i for i in range(1, 101)] + [i / 100 for i in range(100, 501, 25)])
                Grade.objects.create(
                    subject=subject,
                    grade=grade_value,
                    quarter=quarter,
                    semester=semester,
                    education=education
                )


if __name__ == '__main__':
    # Fetch all orphans, ensure there are some orphans in your database
    orphans = Info.objects.all()
    create_education(100, orphans)  # Generate 100 education records
