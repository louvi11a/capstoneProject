from .models import prac_notes
from django import forms
from .models import Notes


class NoteForm(forms.ModelForm):
    class Meta:
        model = Notes
        fields = ['text']

# prac form


class NoteForm(forms.ModelForm):
    class Meta:
        model = prac_notes
        fields = ['text']
