from faker import Faker
from django.utils import timezone
from django.db import models
# Replace . with your app name (e.g., orphans)
from orphans.models import Info, Education, Subject, Grade
import random
fake = Faker()


def generate_orphans(num_orphans):
    for _ in range(num_orphans):
        info = Info(
            firstName=fake.first_name(),
            # middleName=fake.middle_name(), # Uncomment if you decide to use middle names
            lastName=fake.last_name(),
            gender=random.choice(['male', 'Female']),
            # Random past date within 2 years
            birthDate=fake.date_between(start_date='-2y', end_date='today'),
            dateAdmitted=timezone.now(),  # Set admitted date to today
        )
        info.save()


if __name__ == "__main__":
    generate_orphans(15)  # Change 100 to your desired number of orphans


def generate_education_data(orphan, num_entries=1):
    EDUCATION_LEVEL_CHOICES = ['Elementary', 'High School', 'College']
    for _ in range(num_entries):
        education = models.Education(
            orphan=orphan,
            education_level=random.choice(EDUCATION_LEVEL_CHOICES),
            # Generate a fake company name as a placeholder for school name
            school_name=fake.company(),
            year_level=random.randint(1, 12) if random.choice(
                EDUCATION_LEVEL_CHOICES) != 'College' else None,
            # Add other fields as necessary
        )
        education.save()
