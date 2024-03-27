from orphans.models import Info, PhysicalHealth, IncidentType, BMI
from django.utils import timezone
from faker import Faker
import random
from orphans.models import Info
from orphans.models import Files
from orphans.models import BMICategory

fake = Faker()


def add_fake_files():
    file_name = fake.file_name()
    file_description = fake.text()
    file_path = fake.file_path()
    is_archived = fake.boolean()
    file = Files.objects.create(
        fileName=file_name,
        fileDescription=file_description,
        filePath=file_path,
        is_archived=is_archived,
    )
    return file


def add_fake_info():
    file = add_fake_files()
    first_name = fake.first_name()
    middle_name = fake.first_name()
    last_name = fake.last_name()
    gender = random.choice(['M', 'F'])
    birth_date = fake.date_of_birth(minimum_age=1, maximum_age=18)
    date_admitted = fake.date_this_decade()
    ethnicity = fake.word()
    info = Info.objects.create(
        orphanFileID=file,
        firstName=first_name,
        middleName=middle_name,
        lastName=last_name,
        gender=gender,
        birthDate=birth_date,
        dateAdmitted=date_admitted,
        ethnicity=ethnicity,
    )
    return info


def create_fake_bmi_category():
    category = fake.random_element(elements=(
        '< 18.5',
        '18.5 - 24.9',
        '25 - 29.9',
        '30 or more',
    ))
    BMICategory.objects.create(category=category)


def create_fake_physical_health():
    orphans = Info.objects.all()
    bmi_categories = BMICategory.objects.all()
    for incident_type in IncidentType.INCIDENT_CHOICES:
        IncidentType.objects.get_or_create(type=incident_type[0])
    incident_types = IncidentType.objects.all()
    for orphan in orphans:
        BMI.objects.create(
            orphan=orphan,
            height=fake.random_int(min=100, max=200),
            weight=fake.random_int(min=20, max=100),
            incident_count=fake.random_int(min=0, max=10),
            recorded_at=fake.date_between(start_date='-1y', end_date='today'),
            incident_type=fake.random_element(elements=incident_types),
            bmi_category=fake.random_element(elements=bmi_categories),
        )


fake = Faker()


def create_fake_files(n):
    for _ in range(n):
        Files.objects.create(
            fileName=fake.file_name(),
            fileDescription=fake.text(),
            filePath=fake.file_path(),
            is_archived=fake.boolean()
        )


# Call the function to create n fake files
create_fake_files(5)
