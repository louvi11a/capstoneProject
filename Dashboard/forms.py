import datetime
from django import forms
from datetime import datetime  # Adjusted import
from django.apps import apps
from orphans.models import Intervention
from django import forms


class InterventionForm(forms.ModelForm):
    class Meta:
        model = Intervention  # ensure this references the correct Intervention model
        fields = ['description', 'status']  # include 'status' field
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
