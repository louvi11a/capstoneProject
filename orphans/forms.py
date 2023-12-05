from django import forms
from .models import Files


class FilesForm(forms.ModelForm):
    class Meta:
        model = Files
        # Add your file field here
        fields = ('fileName', 'fileDescription', 'file', )
