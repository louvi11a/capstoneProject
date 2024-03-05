from django.db import models
from django.conf import settings
from django.urls import reverse
from simple_history.models import HistoricalRecords

# Create your models here.


class Files(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    fileID = models.AutoField(primary_key=True)
    fileName = models.CharField(max_length=255, blank=True, null=True)
    fileDescription = models.TextField(blank=True, null=True)
    is_archived = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(
        null=True, blank=True)  # New field for time deletion

    # Field for the uploaded file
    file = models.FileField(upload_to='uploads/')

    class Meta:
        db_table = 'orphan_files'

    def __str__(self):
        return self.fileName

    def get_absolute_url(self):
        return reverse('files_detail', args=[str(self.fileID)])


GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
]


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
    orphanID = models.AutoField(primary_key=True)
    firstName = models.CharField(max_length=255, blank=True, null=True)
    middleName = models.CharField(max_length=255, blank=True, null=True)
    lastName = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    birthDate = models.DateField(blank=True, null=True)
    dateAdmitted = models.DateField(blank=True, null=True)
    # mothersName = models.CharField(max_length=255, blank=True, null=True)
    # fathersName = models.CharField(max_length=255, blank=True, null=True)
    # homeAddress = models.CharField(max_length=255, blank=True, null=True)

    orphan_picture = models.ImageField(
        upload_to='orphan_pictures/',  blank=True, null=True)
    family = models.ForeignKey(
        Family, on_delete=models.SET_NULL, null=True, blank=True)

    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'orphan_infos'

    def __str__(self):
        return self.firstName or 'No name'

    def get_absolute_url(self):
        return reverse('info_detail', args=[str(self.orphanID)])


# class BMICategory(models.Model):
#     category = models.CharField(max_length=50, choices=(
#         ('< 18.5', 'Underweight'),
#         ('18.5 - 24.9', 'Normal Weight'),
#         ('25 - 29.9', 'Overweight'),
#         ('30 or more', 'Obesity'),
#     ))


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


class PhysicalHealth(models.Model):
    healthID = models.AutoField(primary_key=True)
    orphan = models.OneToOneField(
        'Info', on_delete=models.PROTECT, related_name='physical_health')
    height = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True)
    weight = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True)
    incident_count = models.IntegerField(blank=True, null=True)
    recorded_at = models.DateField(auto_now=True)

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
        db_table = 'orphan_health'

    def calculate_bmi(self):
        if self.height is not None and self.weight is not None:
            height_m = self.height / 100  # convert cm to m
            bmi = self.weight / (height_m ** 2)
            if bmi < 18.5:
                self.bmi_category = 'Underweight'
            elif bmi < 25:
                self.bmi_category = 'Normal Weight'
            elif bmi < 30:
                self.bmi_category = 'Overweight'
            else:
                self.bmi_category = 'Obesity'


class Education(models.Model):
    EDUCATION_LEVEL_CHOICES = [
        ('Elementary', 'Elementary'),
        ('High School', 'High School'),
        ('College', 'College'),
    ]

    QUARTER_CHOICES = [
        (1, 'First Quarter'),
        (2, 'Second Quarter'),
        (3, 'Third Quarter'),
        (4, 'Fourth Quarter'),
    ]

    orphan = models.ForeignKey(
        Info, on_delete=models.CASCADE, related_name='educations')
    education_level = models.CharField(
        max_length=20,  # Adjust the max_length to fit the longest choice
        choices=EDUCATION_LEVEL_CHOICES,
        blank=True,
        null=True
    )
    school_name = models.CharField(max_length=255)
    current_gpa = models.DecimalField(
        max_digits=5, decimal_places=3, null=True, blank=True)
    date_recorded = models.DateField(auto_now_add=True)
    quarter = models.IntegerField(
        choices=QUARTER_CHOICES, null=True, blank=True)
    school_year = models.CharField(max_length=9)  # Add this line
    history = HistoricalRecords()
