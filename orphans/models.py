import logging
from calendar import monthrange
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.urls import reverse
from simple_history.models import HistoricalRecords
from django.db.models import Q, Avg
from django.http import JsonResponse
from django.views import View
from datetime import date, datetime, timedelta, timezone
from django.utils import timezone
from django.db.models import Avg
from django.db.models import Prefetch
from datetime import timedelta

logger = logging.getLogger(__name__)

# Fetch health details with related orphan info preloaded


class Family(models.Model):
    mother_name = models.CharField(max_length=255, blank=True, null=True)
    mother_dob = models.DateField(blank=True, null=True)
    mother_contact = models.CharField(max_length=255, blank=True, null=True)
    mother_occupation = models.CharField(max_length=255, blank=True, null=True)
    mother_address = models.CharField(max_length=255, blank=True, null=True)
    mother_status = models.CharField(max_length=255, blank=True, null=True)

    father_name = models.CharField(max_length=255, blank=True, null=True)
    father_dob = models.DateField(blank=True, null=True)
    father_contact = models.CharField(max_length=255, blank=True, null=True)
    father_occupation = models.CharField(max_length=255, blank=True, null=True)
    father_address = models.CharField(max_length=255, blank=True, null=True)
    father_status = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'family_infos'


class OrphanFiles(models.Model):
    TYPE_OF_DOCUMENT_CHOICES = [
        ('Birth Certificate', 'Birth Certificate'),
        ('Identification', 'Identification'),
        ('Medical Certificates', 'Medical Certificates'),
        ('Grade Cards', 'Grade Cards'),
        ('Other Documents', 'Other Documents'),
    ]

    orphan = models.ForeignKey(
        'Info', on_delete=models.CASCADE, related_name='orphan_files')
    file = models.FileField(upload_to='orphan_files/')
    file_name = models.CharField(max_length=255)
    type_of_document = models.CharField(
        max_length=55, choices=TYPE_OF_DOCUMENT_CHOICES)
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'orphan_files'

    def __str__(self):
        return self.file_name


class Files(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    fileID = models.AutoField(primary_key=True)
    fileName = models.CharField(max_length=255, blank=True, null=True)
    fileDescription = models.TextField(blank=True, null=True)
    is_archived = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(
        null=True, blank=True)  # New field for time deletion
    file = models.FileField(upload_to='uploads/', blank=True, null=True)

    class Meta:
        db_table = 'general_files'

    def __str__(self):
        return self.fileName

    def get_absolute_url(self):
        return reverse('files_detail', args=[str(self.fileID)])


class Notes(models.Model):
    note_id = models.AutoField(primary_key=True)
    # orphan_id = models.IntegerField()
    text = models.TextField()
    translated_note = models.TextField(blank=True, null=True)  # English notes
    sentiment_score = models.FloatField(null=True)  # Allow NULL values
    timestamp = models.DateTimeField(auto_now_add=True)

    related_orphan = models.ForeignKey(
        'orphans.Info', on_delete=models.CASCADE, related_name='notes')

    def __str__(self):
        return f"Note #{self.id} (Orphan ID: {self.related_orphan.id})"

    class Meta:
        db_table = "OrphanBehavior_notes"


class Info(models.Model):
    STATUS_CHOICES = (
        ('P', 'Pending'),
        ('A', 'Admitted'),
        ('G', 'Graduated'),
    )
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]
    orphanID = models.AutoField(primary_key=True)
    firstName = models.CharField(max_length=255, blank=True, null=True)
    middleName = models.CharField(max_length=255, blank=True, null=True)
    lastName = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(
        max_length=6, choices=GENDER_CHOICES, blank=True, null=True)
    birthDate = models.DateField(blank=True, null=True)
    dateAdmitted = models.DateField(blank=True, null=True)
    age = models.IntegerField(null=True, blank=True)

    orphan_picture = models.ImageField(
        upload_to='orphan_pictures/',  blank=True, null=True)
    family = models.ForeignKey(
        'Family', on_delete=models.SET_NULL, null=True, blank=True)

    is_deleted = models.BooleanField(default=False)
    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, default='P')

    class Meta:
        db_table = 'orphan_infos'

    def __str__(self):
        return self.firstName or 'No name'

    # checks if an orphan has birth certificate and sets a status
    def has_birth_certificate(self):
        return self.orphan_files.filter(type_of_document='Birth Certificate').exists()

    def get_dynamic_status(self):
        return "Admitted" if self.has_birth_certificate() else "Pending"

    def get_absolute_url(self):
        url = reverse('orphan_profile', kwargs={'orphanID': self.orphanID})
        print(f"Generated URL: {url}")  # Debugging print
        return url

    @property
    # Calculates the average sentiment score from the notes associated with the orphan for the current month.
    def average_sentiment(self):
        current_month = timezone.now().date().replace(day=1)
        recent_notes = self.notes.filter(
            timestamp__year=current_month.year, timestamp__month=current_month.month)
        avg_sentiment = recent_notes.aggregate(Avg('sentiment_score'))[
            'sentiment_score__avg']
        return avg_sentiment if avg_sentiment is not None else 0

    def calculate_age(self):
        if self.birthDate:
            today = date.today()
            return today.year - self.birthDate.year - ((today.month, today.day) < (self.birthDate.month, self.birthDate.day))
        else:
            return None

    def determine_age_range(self):
        age = self.calculate_age()
        if age is None:
            return "Unknown"
        elif age <= 10:
            return '0-10'
        elif age <= 20:
            return '11-20'
        elif age <= 30:
            return '21-30'
        # Add more conditions as necessary
        else:
            return "30+"

    def save(self, *args, **kwargs):
        self.age = self.calculate_age()  # Call your calculate_age method
        super().save(*args, **kwargs)  # Call the original save method


# Calculates a behavior score based on sentiment scores from notes, applying a decay factor to give more importance to recent entries.

    def calculate_behavior_score(self, last_months=4):
        current_date = datetime.now().date()
        past_date = current_date - timedelta(days=last_months * 30)

        # Filter notes that are newer than 'past_date'
        notes = self.notes.filter(
            timestamp__date__gte=past_date).order_by('-timestamp')

        current_date = datetime.now().date()
        behavior_score = 0
        total_weight = 0
        decay_rate = 0.1  # Adjust based on how quickly you want to discount older notes

        for note in notes:
            # Calculate days since the note was created
            days_since_note = (current_date - note.timestamp.date()).days
            # Apply a decay factor for recency, making recent notes more influential
            time_weight = pow((1 - decay_rate), days_since_note)
            # Standardize the sentiment score to a 0-100 scale
            # Convert from -1—1 to 0—100 scale
            standardized_sentiment_score = (note.sentiment_score + 1) * 50
            # Accumulate the weighted score
            behavior_score += standardized_sentiment_score * time_weight
            # Keep track of the total weight for normalization
            total_weight += time_weight

        # Normalize the behavior score if there are notes
        if total_weight > 0:
            behavior_score /= total_weight

        return behavior_score

# Computes an average score from the educational records related to the orphan.
    def calculate_education_score(self, last_months=4):

        current_date = datetime.now()
        # Approximate the date 4 months ago
        past_date = current_date - timedelta(days=last_months * 30)

        # Retrieve all Education instances related to this orphan
        educations = self.educations.filter(date_recorded__gte=past_date)

        if not educations:
            return Decimal(0)  # Or some default score if appropriate

        total_score = 0
        count = 0

        # Iterate through each Education instance
        for education in educations:
            # Get all Grade instances related to this Education instance
            grades = education.grades.all()

            # Skip if there are no grades for this Education instance
            if not grades.exists():
                continue

            # Calculate the average of standardized grades for this Education instance
            education_score = sum([grade.standardize_grade()
                                  for grade in grades]) / grades.count()

            # Add this average to the total score
            total_score += education_score

            # Increment count
            count += 1

        # Calculate the overall average score if there were any grades
        if count > 0:
            return total_score / count

        return None  # Or some default score if appropriate

#  Analyzes trends for specified parameters (education, physical wellbeing, behavior) over time, using a moving average to determine if the situation is improving, worsening, or stable.
    def calculate_trend(self, parameter_name):
        if parameter_name == 'education':
            # Assuming an Education model exists and has a foreign key to Info
            scores = self.education_set.all().order_by(
                'timestamp').values_list('score', flat=True)
        elif parameter_name == 'physical_wellbeing':
            # Similar approach for physical_wellbeing
            scores = self.physical_health.all().order_by(
                'timestamp').values_list('composite_score', flat=True)
        elif parameter_name == 'behavior':
            # And for behavior
            scores = self.notes.all().order_by(
                'timestamp').values_list('sentiment_score', flat=True)
        else:
            return None

        # Example trend analysis: Check if the average score is increasing, decreasing, or stable
        if len(scores) < 2:
            return "Insufficient data"

        scores = [Decimal(score) for score in scores]

        # Calculate the moving average of the last 3 scores
        moving_average = sum(scores[-3:]) / Decimal('3')

        # Compare the moving average with the average of the scores before the last 3
        previous_average = sum(scores[:-3]) / Decimal(max(len(scores) - 3, 1))

        if moving_average > previous_average:
            trend_analysis_result = "improving"
        elif moving_average < previous_average:
            trend_analysis_result = "worsening"
        else:
            trend_analysis_result = "stable"

        return trend_analysis_result


# Determines a status based on a weighted score that considers education, health, and behavior. It adjusts weights based on the health score and provides a final status indicating the level of attention needed.


    def calculate_status(self):
        # Define base weights
        weights = {
            'education': Decimal('0.3'),
            'health': Decimal('0.3'),
            'behavior': Decimal('0.4')
        }

        # Assuming the individual score methods return float, convert them to Decimal
        # Fetch scores
        education_score = Decimal(
            self.calculate_education_score(last_months=4) or 0)
        behavior_score = Decimal(
            self.calculate_behavior_score(last_months=4) or 0)

        # Decide based on your needs which method to use:
        # For more responsive health assessments:
        # health_score = Decimal(HealthDetail.calculate_monthly_health_score(self, current_month, current_year) or 0)
        # For averaging over the last three months:
        health_score = Decimal(
            HealthDetail.calculate_average_health_score(self, months=4) or 0)

        # Apply conditional weightings based on specific criteria
        # if health_score < Decimal('50'):
        #     weights['health'] += Decimal('0.2')
        #     weights['education'] -= Decimal('0.1')
        #     weights['behavior'] -= Decimal('0.1')
        # Add more conditions as necessary

        # Calculate the composite score using Decimal for all arithmetic
        composite_score = (education_score * weights['education'] +
                           health_score * weights['health'] +
                           behavior_score * weights['behavior'])

        # Determine status based on composite score
        if composite_score < Decimal('50'):
            return 'Critical Attention Needed'
        elif composite_score < Decimal('70'):
            return 'Monitoring Required'
        else:
            return 'Stable'


class BaseIntervention(models.Model):
    STATUS_CHOICES = [
        ('resolved', 'Resolved'),
        ('pending', 'Pending'),
        ('unresolved', 'Unresolved'),
        ('none', 'None'),

    ]

    orphan = models.ForeignKey(
        'Info', on_delete=models.CASCADE, related_name='%(class)s')
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='pending')
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AcademicIntervention(BaseIntervention):
    orphan = models.ForeignKey(
        Info, on_delete=models.CASCADE, related_name='academicinterventions')

    # New fields to store baseline data at the time of intervention resolution
    baseline_critical = models.BooleanField(
        default=False, help_text="Indicates if critical improvement was needed at the time of resolving the intervention.")
    baseline_significant = models.BooleanField(
        default=False, help_text="Indicates if significant improvement was needed at the time of resolving the intervention.")

    def save(self, *args, **kwargs):
        # Automatically set baseline data when an intervention is resolved
        if self.status == 'resolved' and not self.pk:
            self.set_baseline_data()
        super().save(*args, **kwargs)

    def set_baseline_data(self):
        # Logic to determine if critical or significant improvements are needed at the time of resolution
        # This method should be defined based on how you determine 'critical_needed' and 'significant_needed'
        self.baseline_critical = self.determine_critical_needed()
        self.baseline_significant = self.determine_significant_needed()

    def determine_critical_needed(self):
        # Placeholder method - implement the logic to determine if critical improvement is needed
        return any(grade.grade < 70 for education in self.orphan.educations.all() for grade in education.grades.all())

    def determine_significant_needed(self):
        # Placeholder method - implement the logic to determine if significant improvement is needed
        return any(70 <= grade.grade < 75 for education in self.orphan.educations.all() for grade in education.grades.all())


class BehaviorIntervention(BaseIntervention):
    orphan = models.ForeignKey(
        Info, on_delete=models.CASCADE, related_name='behaviorinterventions')
    baseline_sentiment = models.FloatField(
        null=True, blank=True, help_text="Sentiment score at the time of resolving the intervention.")

    def save(self, *args, **kwargs):
        if self.status == 'resolved' and self.baseline_sentiment is None:
            # Assuming you have a method to calculate the current sentiment or it's passed in some way
            self.baseline_sentiment = self.calculate_current_sentiment()
        super().save(*args, **kwargs)

    def calculate_current_sentiment(self):
        # Placeholder for sentiment calculation logic
        # You would need to define how to calculate this based on your application's requirements
        return 0.0  # Example default value

    # other fields...


class HealthIntervention(BaseIntervention):
    orphan = models.ForeignKey(
        Info, on_delete=models.CASCADE, related_name='healthinterventions')

    # Add fields to store baseline health status
    baseline_health_score = models.FloatField(
        null=True, blank=True, help_text="Health score at the time of resolving the intervention.")

    def save(self, *args, **kwargs):
        if self.status == 'resolved' and self.baseline_health_score is None:
            # This assumes there's a method to calculate the health score that needs to be reliably available
            self.baseline_health_score = self.calculate_current_health_score()
        super().save(*args, **kwargs)

    def calculate_current_health_score(self):
        # Placeholder method - implement based on your application's health scoring logic
        return 0.0  # Example default value

    # other fields...


# class InterventionHistory(models.Model):
#     intervention = models.ForeignKey(
#         # Key Change: Use string reference here
#         'BaseIntervention', on_delete=models.CASCADE, related_name='history'
#     )
#     status = models.CharField(
#         max_length=10, choices=BaseIntervention.STATUS_CHOICES
#     )
#     description = models.TextField()
#     date_created = models.DateTimeField(auto_now_add=True)


def get_sentiment_data():
    orphans = Info.objects.all()
    positive = 0
    negative = 0
    neutral = 0

    for orphan in orphans:
        avg_sentiment = orphan.average_sentiment
        if avg_sentiment is None:
            continue  # skip orphans with no notes for the current month
        elif avg_sentiment > 0.05:  # Threshold for positive
            positive += 1
        elif avg_sentiment < -0.05:  # Threshold for negative
            negative += 1
        else:
            neutral += 1

    return positive, negative, neutral


def intervention_behavior_count():
    orphans = Info.objects.all()
    negative = 0

    for orphan in orphans:
        avg_sentiment = orphan.average_sentiment
        if avg_sentiment is not None and avg_sentiment < -0.05:  # adjust these values as needed
            negative += 1

    return negative


class HealthDetail(models.Model):
    resolved = models.DateField(null=True, blank=True)
    sick_start_date = models.DateField(null=True, blank=True)
    sick_resolved = models.BooleanField(default=False)

    # date = models.DateField()
    temperature = models.DecimalField(max_digits=4, decimal_places=1)
    blood_pressure = models.CharField(max_length=7)
    fever = models.BooleanField(default=False)
    vomiting = models.BooleanField(default=False)
    headache = models.BooleanField(default=False)
    stomachache = models.BooleanField(default=False)
    cough = models.BooleanField(default=False)
    dizziness = models.BooleanField(default=False)
    body_pain = models.BooleanField(default=False)
    # others_symptoms = models.CharField(max_length=255, blank=True, null=True)
    other_details = models.TextField(blank=True, null=True)
    orphan = models.ForeignKey(
        'Info', on_delete=models.CASCADE, related_name='health_details')

    def __str__(self):
        return f"Health Details for {self.orphan.firstName}, Resolved on {self.resolved}"

    def is_symptom_active(self, symptom_name, check_date):
        # Check if a symptom was active on a given day
        if not self.sick_start_date:  # No sick start date, symptom never active
            return False, 0
        if getattr(self, symptom_name) and check_date >= self.sick_start_date:
            if self.resolved:
                days_active = (self.resolved - self.sick_start_date).days + 1
            else:  # Sickness not yet resolved
                days_active = (check_date - self.sick_start_date).days + 1
            return True, days_active
        else:
            return False, 0

    orphan = models.ForeignKey(
        'Info', on_delete=models.CASCADE, related_name='health_details')

    def __str__(self):
        return f"Health Details for {self.orphan.firstName}, Resolved on {self.resolved}"

    @staticmethod
    def calculate_average_health_score(orphan, months=4):
        current_date = date.today()
        scores = []

        for i in range(months):
            # Calculate the month and year for each month going backwards
            month_year = (current_date.month - i - 1) % 12 + 1
            year = current_date.year if (
                current_date.month - i - 1) >= 0 else current_date.year - 1

            # Adjust for the month/year roll-over
            if current_date.month - i - 1 < 0:
                year -= 1

            score = HealthDetail.calculate_monthly_health_score(
                orphan, month_year, year)
            scores.append(score)

        if scores:
            return sum(scores) / len(scores) if scores else 0
        return 0

    def calculate_monthly_health_score(orphan, month, year):
        def calculate_weights(days_in_month):
            """Calculates weights for each day of the month, giving more weight to recent days.
            This uses a linear decay.
            """
            weights = [i / days_in_month for i in range(days_in_month, 0, -1)]
            return weights

        SYMPTOM_SCORES = {
            'fever': 5,
            'vomiting': 4,
            'headache': 4,
            'stomachache': 4,
            'cough': 4,
            'dizziness': 4,
            'body_pain': 4
        }

        DURATION_THRESHOLDS = [
            (3, 1.5),  # 1-3 days: Multiplier of 1.5
            (7, 2.5),  # 4-7 days: Multiplier of 2
            (14, 3.5),  # 1 week to 2 weeks: Multiplier of 2.5
            (None, 4)  # More than 2 weeks: Multiplier of 3
        ]

        try:
            from calendar import monthrange
            from datetime import date, timedelta

            # Ensure month is within the valid range
            if not 1 <= month <= 12:
                logger.error(
                    f"Invalid month passed to calculate_monthly_health_score: {month}")
                raise ValueError("Month must be in 1..12")

            start_of_month = date(year, month, 1)
            days_in_month = monthrange(year, month)[1]
            end_of_month = start_of_month + timedelta(days=days_in_month - 1)

            daily_scores = []
            # Get weights for each day
            weights = calculate_weights(days_in_month)

            for single_date, weight in zip((start_of_month + timedelta(n) for n in range(days_in_month)), weights):
                daily_score = 100
                symptoms_today = HealthDetail.objects.filter(
                    orphan=orphan, sick_start_date=single_date)

                active_symptom_count = sum(detail.is_symptom_active(symptom, single_date)[0]
                                           for detail in symptoms_today for symptom in SYMPTOM_SCORES)
                severity_factor = 1 + (active_symptom_count * 0.25)

                for detail in symptoms_today:
                    for symptom in SYMPTOM_SCORES:
                        is_active, duration = detail.is_symptom_active(
                            symptom, single_date)
                        if is_active:
                            base_score = SYMPTOM_SCORES[symptom]
                            for days_threshold, multiplier in DURATION_THRESHOLDS:
                                if days_threshold is None or duration <= days_threshold:
                                    symptom_score = base_score * severity_factor * multiplier
                                    break
                            daily_score -= symptom_score

                daily_scores.append(max(daily_score, 0) *
                                    weight)  # Apply weight

            weighted_average_score = sum(daily_scores) / sum(weights)
            return weighted_average_score

        except ValueError as e:
            logger.error(
                f"Date error in calculate_monthly_health_score: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in calculate_monthly_health_score for orphan {
                orphan.orphanID}: {str(e)}")
            raise


health_details = HealthDetail.objects.prefetch_related(
    Prefetch('orphan', queryset=Info.objects.all())
)


class IncidentType(models.Model):
    INCIDENT_CHOICES = (
        ('Accident', 'Accident'),
        ('Illness', 'Illness'),
        ('Injury', 'Injury'),
        ('Other', 'Other'),
    )

    type = models.CharField(
        max_length=50, choices=INCIDENT_CHOICES, unique=True)

    def __str__(self):
        return self.type


class BMI(models.Model):
    bmi_ID = models.AutoField(primary_key=True)
    orphan = models.ForeignKey(
        'Info', on_delete=models.CASCADE, related_name='physical_health')
    height = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True)
    weight = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True)
    bmi = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True)

    incident_count = models.IntegerField(blank=True, null=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    BMI_CATEGORIES = [
        ('< 18.5', 'Underweight'),
        ('18.5 - 24.9', 'Normal Weight'),
        ('25 - 29.9', 'Overweight'),
        ('30 or more', 'Obesity'),
    ]

    bmi_category = models.CharField(
        max_length=20,
        choices=BMI_CATEGORIES,
        blank=True,
        null=True
    )

    incident_type = models.ForeignKey(
        IncidentType, on_delete=models.CASCADE, blank=True, null=True)

    history = HistoricalRecords()

    class Meta:
        db_table = 'orphan_BMI'
        ordering = ['-recorded_at']  # Order by recorded_at in descending order

    def calculate_bmi(self):
        if self.height is not None and self.weight is not None:
            height_m = self.height / 100  # convert cm to m
            bmi = self.weight / (height_m ** 2)
            bmi = round(bmi, 2)  # Round the BMI value to two decimal places

            self.bmi = bmi  # Store the calculated BMI value
            self.save()  # Save the model instance to persist the BMI value
            if bmi < 18.5:
                self.bmi_category = 'Underweight'
            elif bmi < 25:
                self.bmi_category = 'Normal Weight'
            elif bmi < 30:
                self.bmi_category = 'Overweight'
            else:
                self.bmi_category = 'Obesity'
            return bmi  # Return the calculated BMI value

    def calculate_standardized_bmi_score(self):
        # Define the scoring for each BMI category
        scores_by_category = {
            'Underweight': 75,
            'Normal Weight': 100,
            'Overweight': 75,
            'Obesity': 50,
        }

        # Get the score for the BMI category of this instance
        bmi_score = scores_by_category.get(self.bmi_category, 0)

        # Assuming each incident reduces the score by a certain amount
        INCIDENT_SCORE_PENALTY = 5  # define the penalty for each incident

        # Check if self.incident_count is None and set it to 0 if it is
        incident_count = self.incident_count if self.incident_count is not None else 0

        # Calculate the incident penalty
        incident_penalty = min(incident_count * INCIDENT_SCORE_PENALTY, 100)

        # Calculate final BMI score by subtracting incident penalties
        final_bmi_score = max(0, bmi_score - incident_penalty)
        return final_bmi_score


class Subject(models.Model):
    name = models.CharField(max_length=255)


class Education(models.Model):
    EDUCATION_LEVEL_CHOICES = [
        ('Elementary', 'Elementary'),
        ('High School', 'High School'),
        ('College', 'College'),
    ]

    orphan = models.ForeignKey(
        'Info', on_delete=models.CASCADE, related_name='educations')
    education_level = models.CharField(
        max_length=20,  # Adjust tge max_length to fit the longest choice
        choices=EDUCATION_LEVEL_CHOICES,
        blank=True,
        null=True
    )
    school_name = models.CharField(max_length=255)
    year_level = models.IntegerField(null=True, blank=True)

    current_gpa = models.DecimalField(
        max_digits=5, decimal_places=3, null=True, blank=True)
    date_recorded = models.DateField(auto_now_add=True)
    subjects = models.ManyToManyField(Subject, through='Grade')
    history = HistoricalRecords()


class Grade(models.Model):
    GRADE_CHOICES = [(i, i) for i in range(1, 101)] + [(i/100, i/100)
                                                       # Grades from 1 to 100 and 1.00 to 5.00
                                                       for i in range(100, 501, 25)]

    QUARTER_CHOICES = [
        (1, 'First Quarter'),
        (2, 'Second Quarter'),
        (3, 'Third Quarter'),
        (4, 'Fourth Quarter'),
    ]
    SEMESTER_CHOICES = [
        (1, 'First Semester'),
        (2, 'Second Semester'),
    ]

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    grade = models.DecimalField(
        choices=GRADE_CHOICES, max_digits=5, decimal_places=2)

    quarter = models.IntegerField(
        choices=QUARTER_CHOICES, null=True, blank=True)
    semester = models.IntegerField(
        choices=SEMESTER_CHOICES, null=True, blank=True)
    education = models.ForeignKey(
        Education, on_delete=models.CASCADE, related_name='grades')

# Converts different scoring formats (like letters) into a standard numeric format for easier analysis.
    def standardize_grade(self):
        # Convert float literals to Decimal
        high_school_max_score = Decimal('100')
        high_school_min_passing_score = Decimal('75')
        college_max_score = Decimal('1.00')
        college_min_score = Decimal('5.00')

        education_level = self.education.education_level

        if education_level == 'College':
            if self.grade >= college_min_score:
                # Return a Decimal value
                return high_school_min_passing_score - Decimal('1')
            # Ensure all operands are Decimal instances
            standardized_grade = ((high_school_max_score - high_school_min_passing_score) /
                                  (college_min_score - college_max_score)) * (self.grade - college_max_score) + high_school_max_score
            standardized_grade = min(standardized_grade, high_school_max_score)
        else:  # Elementary or High School
            if self.grade < high_school_min_passing_score:
                return self.grade
            standardized_grade = self.grade  # No conversion needed

        return standardized_grade
