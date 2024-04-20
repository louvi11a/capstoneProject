
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from faker import Faker
from datetime import timedelta
import random
from orphans.models import Info, HealthDetail


class Command(BaseCommand):
    help = 'Generate realistic health details for each Info instance.'

    def handle(self, *args, **options):
        fake = Faker()

        for info in Info.objects.all():
            start_date = fake.date_between(start_date='-2y', end_date='today')
            resolved_date = start_date + \
                timedelta(days=random.randint(1, 90)) if random.choice(
                    [True, False]) else None
            if resolved_date and resolved_date > now().date():
                resolved_date = None  # Ensure resolved date is not in the future

            health_detail = HealthDetail.objects.create(
                orphan=info,
                sick_start_date=start_date,
                resolved=resolved_date,
                sick_resolved=bool(resolved_date),
                temperature=random.uniform(36.0, 39.9),
                blood_pressure=f"{random.randint(
                    100, 130)}/{random.randint(60, 90)}",
                fever=random.choice([True, False]),
                vomiting=random.choice([True, False]),
                headache=random.choice([True, False]),
                stomachache=random.choice([True, False]),
                cough=random.choice([True, False]),
                dizziness=random.choice([True, False]),
                body_pain=random.choice([True, False]),
                other_details=fake.sentence() if random.choice(
                    [True, False]) else ""
            )

            self.stdout.write(self.style.SUCCESS(f'Successfully created health detail for {
                              info} with start date {start_date} and resolved date {resolved_date}.'))
