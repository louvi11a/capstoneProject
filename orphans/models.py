from django.db import models
from django.conf import settings


# Create your models here.


class Files(models.Model):
    fileID = models.AutoField(primary_key=True)
    fileName = models.CharField(max_length=255, blank=True, null=True)
    fileDescription = models.TextField(blank=True, null=True)
    filePath = models.CharField(max_length=255, blank=True, null=True)
    is_archived = models.BooleanField(default=False)

    # new field for the uploaded file
    file = models.FileField(upload_to='uploads/')

    class Meta:
        db_table = 'orphan_files'

    def __str__(self):
        return self.fileName


class Info(models.Model):
    orphanID = models.AutoField(primary_key=True)
    firstName = models.CharField(max_length=255, blank=True, null=True)
    middleName = models.CharField(max_length=255, blank=True, null=True)
    lastName = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=1, blank=True, null=True)
    birthDate = models.DateField(blank=True, null=True)
    dateAdmitted = models.DateField(blank=True, null=True)
    ethnicity = models.CharField(max_length=255, blank=True, null=True)
    orphan_picture = models.ImageField(
        upload_to='orphan_pictures/',  blank=True, null=True)

    # Define ForeignKey relationships
    # orphanbehaviorID = models.ForeignKey(
    #     'behavior.Notes', on_delete=models.PROTECT, db_column='orphanbehaviorID')
    orphanFileID = models.ForeignKey(
        'orphans.Files', on_delete=models.PROTECT, db_column='orphanFileID')

    class Meta:
        db_table = 'orphan_infos'

    def __str__(self):
        return self.firstName


class BMICategory(models.Model):
    category = models.CharField(max_length=50, choices=(
        ('< 18.5', 'Underweight'),
        ('18.5 - 24.9', 'Normal Weight'),
        ('25 - 29.9', 'Overweight'),
        ('30 or more', 'Obesity'),
    ))


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
    # fkey
    orphan = models.OneToOneField(
        'Info', on_delete=models.PROTECT, related_name='physical_health')
    height = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True)
    weight = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True)
    incident_count = models.IntegerField(blank=True, null=True)
    recorded_at = models.DateField(blank=True, null=True)

    # fkey
    incident_type = models.ForeignKey(
        IncidentType, on_delete=models.CASCADE, blank=True, null=True)
    bmi_category = models.ForeignKey(
        BMICategory, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'orphan_health'
