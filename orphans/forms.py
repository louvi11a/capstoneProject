import datetime
from django import forms
from .utils import get_school_year_choices
from datetime import datetime  # Adjusted import
from . import models


class OrphanFileForm(forms.ModelForm):
    class Meta:
        model = models.OrphanFiles
        fields = ['orphan', 'file', 'file_name',
                  'type_of_document', 'description']


class NoteForm(forms.ModelForm):
    class Meta:
        model = models.Notes
        fields = ['text']


class OrphanForm(forms.ModelForm):
    class Meta:
        model = models.Info
        fields = ['gender', 'firstName', 'middleName', 'lastName', 'birthDate', 'dateAdmitted',
                  'orphan_picture']


# class UploadBirthCertificateForm(forms.Form):
#     birth_certificate = forms.FileField()


class FilesForm(forms.ModelForm):
    class Meta:
        model = models.Files
        # Add your file field here
        fields = ('fileName', 'fileDescription', 'file', )


# forms.py

class FamilyForm(forms.ModelForm):
    class Meta:
        model = models.Family
        fields = ['mother_name', 'mother_dob', 'mother_contact', 'mother_occupation', 'mother_address', 'mother_status',
                  'father_name', 'father_dob', 'father_contact', 'father_occupation', 'father_address', 'father_status']


class OrphanProfileForm(forms.ModelForm):
    class Meta:
        model = models.Info
        fields = ['orphanID', 'firstName', 'middleName', 'lastName', 'gender',
                  'birthDate', 'dateAdmitted', 'orphan_picture', 'is_deleted']


class BmiForm(forms.ModelForm):
    class Meta:
        model = models.BMI
        fields = ['height', 'weight']


def get_school_years_choices():
    current_year = datetime.now().year

    # Generates choices for the current and next year as an example
    return [(f"{year}-{year+1}", f"{year}-{year+1}") for year in range(current_year - 5, current_year + 5)]


class EducationForm(forms.ModelForm):
    # school_year = forms.ChoiceField(choices=[])

    class Meta:
        model = models.Education
        fields = ['education_level', 'school_name',
                  'year_level', 'current_gpa']


class GradeForm(forms.ModelForm):
    class Meta:
        model = models.Grade
        fields = ['subject', 'grade', 'semester', 'quarter',]
