from django.db import models
from django.conf import settings
from django.urls import reverse
from simple_history.models import HistoricalRecords
from django.db.models import Q, Avg
from django.http import JsonResponse
from django.views import View
from datetime import date


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
        Family, on_delete=models.SET_NULL, null=True, blank=True)

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
