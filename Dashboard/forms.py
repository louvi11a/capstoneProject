import datetime
from django import forms
from datetime import datetime  # Adjusted import
from django.apps import apps
from orphans.models import AcademicIntervention, BehaviorIntervention, HealthIntervention
from django import forms


class AcademicInterventionForm(forms.ModelForm):
    class Meta:
        model = AcademicIntervention  # ensure this references the correct Intervention model
        fields = ['description', 'status']  # include 'status' field
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class BehaviorInterventionForm(forms.ModelForm):
    class Meta:
        model = BehaviorIntervention
        fields = ['description', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class HealthInterventionForm(forms.ModelForm):
    class Meta:
        model = HealthIntervention
        fields = ['description', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
