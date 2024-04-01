import datetime
from .models import Family, Grade
from .models import Info
from django import forms
from .models import Files, Education, Info, BMI
from .utils import get_school_year_choices
from datetime import datetime  # Adjusted import

from .models import Notes


class NoteForm(forms.ModelForm):
    class Meta:
        model = Notes
        fields = ['text']


class OrphanForm(forms.ModelForm):
    class Meta:
        model = Info
        fields = ['gender', 'firstName', 'middleName', 'lastName', 'birthDate', 'dateAdmitted',
                  'orphan_picture', 'birth_certificate']


# class UploadBirthCertificateForm(forms.Form):
#     birth_certificate = forms.FileField()


class FilesForm(forms.ModelForm):
    class Meta:
        model = Files
        # Add your file field here
        fields = ('fileName', 'fileDescription', 'file', )


# forms.py

class FamilyForm(forms.ModelForm):
    class Meta:
        model = Family
        fields = ['mother_name', 'mother_dob', 'mother_contact', 'mother_occupation', 'mother_address', 'mother_status',
                  'father_name', 'father_dob', 'father_contact', 'father_occupation', 'father_address', 'father_status']


class OrphanProfileForm(forms.ModelForm):
    class Meta:
        model = Info
        fields = ['orphanID', 'firstName', 'middleName', 'lastName', 'gender',
                  'birthDate', 'dateAdmitted', 'orphan_picture', 'is_deleted']


class BmiForm(forms.ModelForm):
    class Meta:
        model = BMI
        fields = ['height', 'weight']


def get_school_years_choices():
    current_year = datetime.now().year

    # Generates choices for the current and next year as an example
    return [(f"{year}-{year+1}", f"{year}-{year+1}") for year in range(current_year - 5, current_year + 5)]


class EducationForm(forms.ModelForm):
    # school_year = forms.ChoiceField(choices=[])

    class Meta:
        model = Education
        fields = ['education_level', 'school_name',
                  'year_level', 'current_gpa']

    # def __init__(self, *args, **kwargs):
    #     super(EducationForm, self).__init__(*args, **kwargs)
    #     self.fields['school_year'].choices = get_school_years_choices()


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['subject', 'grade', 'semester', 'quarter',]
