from .models import Info
from django import forms
from .models import Files


class FilesForm(forms.ModelForm):
    class Meta:
        model = Files
        # Add your file field here
        fields = ('fileName', 'fileDescription', 'file', )


# forms.py


class OrphanProfileForm(forms.ModelForm):
    class Meta:
        model = Info
        fields = [
            'firstName', 'middleName', 'lastName', 'gender', 'birthDate',
            'dateAdmitted', 'mothersName', 'fathersName', 'homeAddress', 'orphan_picture'
        ]
        widgets = {
            'birthDate': forms.DateInput(attrs={'type': 'date'}),
            'dateAdmitted': forms.DateInput(attrs={'type': 'date'}),
        }
