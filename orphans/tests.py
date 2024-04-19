from django.test import TestCase
# Replace 'your_app' with the actual app name
from orphans.models import HealthDetail, Info
from datetime import date


class HealthDetailTestCase(TestCase):

    def test_calculate_monthly_health_score(self):
        # Create an orphan object (if needed)
        orphan = Info.objects.create(firstName="Test", lastName="Orphan")

        # Create mock HealthDetail objects (adjust symptoms, dates, and expected_score)
    try:
        orphan = Info.objects.create(firstName="Test", lastName="Orphan")

        HealthDetail.objects.create(
            orphan=orphan,
            sick_start_date=date(2023, 11, 5),
            resolved=date(2023, 11, 8),
            cough=True,
            temperature=37.5)  # Example temperature)
    except Exception as e:
        print(f"Error creating HealthDetail: {e}")

        # Call the calculate_monthly_health_score function
        score = HealthDetail.calculate_monthly_health_score(orphan, 11, 2023)

        # Assert the expected score (Calculate this based on your scoring logic)
        expected_score = 85  # Replace with the correct calculated score

        self.assertEqual(score, expected_score)
