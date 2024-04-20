from django.core.management.base import BaseCommand
from faker import Faker
import random
from orphans.models import Info, Education, Grade, Subject
from django.utils.timezone import now


class Command(BaseCommand):
    help = 'Generates fake data ensuring every Info record has at least one Grade'

    def handle(self, *args, **options):
        fake = Faker()
        Faker.seed(0)
        subjects = ['Math', 'Science', 'History', 'English', 'Geography']
        subject_objs = [Subject.objects.get_or_create(
            name=sub)[0] for sub in subjects]

        education_details = {
            'College': (1, 4, 1.00, 5.00),
            'High School': (7, 12, 50, 100),
            'Elementary': (1, 6, 50, 100)
        }

        infos = Info.objects.all()
        total_grades = 150
        min_grades_per_info = 1  # Minimum number of grades per Info

        # Calculate grades per Info to evenly distribute
        grades_per_info = max(min_grades_per_info, total_grades // len(infos))
        remaining_grades = total_grades - (grades_per_info * len(infos))

        for info in infos:
            level = random.choice(list(education_details.keys()))
            year_min, year_max, grade_min, grade_max = education_details[level]

            # Ensure at least one Education per Info
            education = Education.objects.create(
                orphan=info,
                education_level=level,
                school_name=fake.company(),
                year_level=random.randint(year_min, year_max),
                date_recorded=now()
            )

            # Assign at least grades_per_info Grades, and distribute remaining grades randomly
            for _ in range(grades_per_info + (1 if remaining_grades > 0 else 0)):
                if level == 'College':
                    semester = random.choice([1, 2])
                    Grade.objects.create(
                        subject=random.choice(subject_objs),
                        grade=random.uniform(grade_min, grade_max),
                        education=education,
                        semester=semester
                    )
                else:
                    quarter = random.choice([1, 2, 3, 4])
                    Grade.objects.create(
                        subject=random.choice(subject_objs),
                        grade=random.randint(int(grade_min), int(grade_max)),
                        education=education,
                        quarter=quarter
                    )
                remaining_grades -= 1 if remaining_grades > 0 else 0

        self.stdout.write(self.style.SUCCESS(
            'Successfully generated fake educational data with 100 grades distributed.'))
