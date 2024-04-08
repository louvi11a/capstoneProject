from django.db import models
from django.conf import settings
from django.urls import reverse
from simple_history.models import HistoricalRecords
from django.db.models import Q, Avg
from django.http import JsonResponse
from django.views import View
from datetime import date, datetime


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
    # # Add a ForeignKey to Info model
    # related_orphan = models.ForeignKey(
    #     'Info', on_delete=models.CASCADE, related_name='files', null=True)
    # Field for the uploaded file
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
    orphan_picture = models.ImageField(
        upload_to='orphan_pictures/',  blank=True, null=True)
    family = models.ForeignKey(
        'Family', on_delete=models.SET_NULL, null=True, blank=True)

    is_deleted = models.BooleanField(default=False)

    def has_birth_certificate(self):
        return self.orphan_files.filter(type_of_document='Birth Certificate').exists()

    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, default='P')

    def get_dynamic_status(self):
        return "Admitted" if self.has_birth_certificate() else "Pending"

    class Meta:
        db_table = 'orphan_infos'

    def __str__(self):
        return self.firstName or 'No name'

    def get_absolute_url(self):
        url = reverse('orphan_profile', kwargs={'orphanID': self.orphanID})
        print(f"Generated URL: {url}")  # Debugging print
        return url

    @property
    def average_sentiment(self):
        return self.notes.aggregate(Avg('sentiment_score'))['sentiment_score__avg']

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

    def calculate_overall_physical_wellbeing(self):
        # Updated weights for BMI and HealthDetail scores
        bmi_weight = 0.3
        health_detail_weight = 0.7

        # Get the latest BMI record and its standardized score
        latest_bmi_record = self.physical_health.last()
        bmi_score = latest_bmi_record.calculate_standardized_bmi_score() if latest_bmi_record else 0

        # Calculate HealthDetail scores with time-decay factor
        health_detail_records = self.health_details.all().order_by('-date')
        current_date = datetime.now().date()
        health_detail_score = 0
        total_weight = 0
        decay_rate = 0.1  # Defines how quickly the weight of older records decays

        for index, detail in enumerate(health_detail_records):
            # Calculate days since the record was created
            days_since_record = (current_date - detail.date).days
            # Apply a decay factor for recency
            time_weight = pow((1 - decay_rate), days_since_record)
            # Accumulate the weighted score
            health_detail_score += detail.calculate_health_score() * time_weight
            # Track the total weight for normalization
            total_weight += time_weight

        # Normalize the health detail score if there are records
        if total_weight > 0:
            health_detail_score /= total_weight

        # Calculate the overall physical well-being score
        overall_score = (bmi_score * bmi_weight) + \
            (health_detail_score * health_detail_weight)
        return overall_score

    def calculate_behavior_score(self):
        # Ensure notes are in descending order by timestamp
        notes = self.notes.all().order_by('-timestamp')
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

    def calculate_education_score(self):
        # Retrieve all Education instances related to this orphan
        educations = self.educations.all()

        if not educations:
            return None  # Or some default score if appropriate

        total_score = 0
        count = 0

        # Iterate through each Education instance
        for education in educations:
            # Get all Grade instances related to this Education instance
            grades = education.grade_set.all()

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

    def calculate_trend(self, parameter_name):
        """
        Calculate the trend of a given parameter over time.
        parameter_name could be 'education', 'physical_wellbeing', 'behavior'
        """
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

        # Calculate the moving average of the last 3 scores
        moving_average = sum(scores[-3:]) / 3

        # Compare the moving average with the average of the scores before the last 3
        previous_average = sum(scores[:-3]) / \
            (len(scores) - 3) if len(scores) > 3 else 0

        if moving_average > previous_average:
            trend_analysis_result = "improving"
        elif moving_average < previous_average:
            trend_analysis_result = "worsening"
        else:
            trend_analysis_result = "stable"

        return trend_analysis_result

    def calculate_composite_score(self):
        # Define weightings
        education_weight = 0.3
        physical_wellbeing_weight = 0.4
        behavior_weight = 0.3

        # Calculate or retrieve individual scores
        # Assuming you have a method or logic to calculate the education score
        education_score = self.calculate_education_score()  # Placeholder for actual method
        if education_score is None:
            return None
        physical_wellbeing_score = self.calculate_overall_physical_wellbeing()
        behavior_score = self.calculate_behavior_score()

        # Calculate the weighted sum of the scores
        composite_score = (education_score * education_weight +
                           physical_wellbeing_score * physical_wellbeing_weight +
                           behavior_score * behavior_weight)

        return composite_score


def get_sentiment_data():
    orphans = Info.objects.all()
    positive = 0
    negative = 0
    neutral = 0

    for orphan in orphans:
        avg_sentiment = orphan.average_sentiment
        if avg_sentiment is None:
            continue  # skip orphans with no notes
        elif avg_sentiment > 0.05:  # adjust these values as needed
            positive += 1
        elif avg_sentiment < -0.05:
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
    date = models.DateField()
    temperature = models.DecimalField(max_digits=4, decimal_places=1)
    blood_pressure = models.CharField(max_length=7)
    heart_rate = models.IntegerField()
    nausea = models.BooleanField(default=False)
    vomiting = models.BooleanField(default=False)
    headache = models.BooleanField(default=False)
    stomachache = models.BooleanField(default=False)
    cough = models.BooleanField(default=False)
    dizziness = models.BooleanField(default=False)
    pain = models.BooleanField(default=False)
    # others_symptoms = models.CharField(max_length=255, blank=True, null=True)
    other_details = models.TextField(blank=True, null=True)

    orphan = models.ForeignKey(
        'Info', on_delete=models.CASCADE, related_name='health_details')

    def __str__(self):
        return f"Health Details for {self.orphan.firstName} on {self.date}"

    def calculate_health_score(self):
        health_score = 100  # Start with a perfect health score

        # Define normal ranges
        # Normal body temperature range in Celsius
        normal_temperature_range = (36.5, 37.5)
        # Normal resting heart rate range in BPM
        normal_heart_rate_range = (60, 100)
        # Normal blood pressure range would be more complex because it has two numbers (systolic and diastolic)

        # Check if the temperature is within the normal range
        if not (normal_temperature_range[0] <= self.temperature <= normal_temperature_range[1]):
            health_score -= 10  # Subtract 10 points if outside normal temperature range

        # Check if the heart rate is within the normal range
        if not (normal_heart_rate_range[0] <= self.heart_rate <= normal_heart_rate_range[1]):
            health_score -= 10  # Subtract 10 points if outside normal heart rate range

        # Add logic to handle blood pressure similar to above, using appropriate thresholds

        # Check for symptoms
        symptoms = [
            self.nausea,
            self.vomiting,
            self.headache,
            self.stomachache,
            self.cough,
            self.dizziness,
            self.pain,
            # Add more if you have other symptoms
        ]
        symptom_penalty = 5  # Penalty points for each symptom
        health_score -= sum(symptom is True for symptom in symptoms) * \
            symptom_penalty

        # If other details are provided, it might indicate additional issues
        if self.other_details:
            health_score -= 10  # Subtract points if there are other details reported

        # Ensure score does not go below 0
        return max(health_score, 0)


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
        ('30 or more', 'Obese'),
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
    # school_year = models.CharField(max_length=9)
    subjects = models.ManyToManyField(Subject, through='Grade')
    history = HistoricalRecords()


class Grade(models.Model):
    GRADE_CHOICES = [(i, i) for i in range(1, 101)]  # Grades from 1 to 100

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
    education = models.ForeignKey(Education, on_delete=models.CASCADE)
    grade = models.IntegerField(choices=GRADE_CHOICES)
    quarter = models.IntegerField(
        choices=QUARTER_CHOICES, null=True, blank=True)
    semester = models.IntegerField(
        choices=SEMESTER_CHOICES, null=True, blank=True)

    def standardize_grade(self):
        # Ensure you reference the education level from the related Education instance
        education_level = self.education.education_level

        # Define the max and min scores for high school
        high_school_max_score = 100
        high_school_min_passing_score = 75

        # Define the max and min passing scores for college
        college_max_score = 1.00
        college_min_score = 3.00

        if education_level == 'College':
            # Assuming college grades are inversely scored (lower is better)
            if self.grade >= college_min_score:
                return high_school_min_passing_score - 1  # Handle failing grades
            # Linear transformation for college grades
            standardized_grade = ((high_school_max_score - high_school_min_passing_score) /
                                  (college_min_score - college_max_score)) * (self.grade - college_max_score) + high_school_max_score
        else:  # Elementary or High School
            # Direct conversion for grades already on a 0-100 scale
            if self.grade < high_school_min_passing_score:
                return self.grade - 1  # Adjust for failing grades
            standardized_grade = self.grade  # No conversion needed

        return standardized_grade
