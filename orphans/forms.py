from .models import Family
from .models import Info
from django import forms
from .models import Files


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
