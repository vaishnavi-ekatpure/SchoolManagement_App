from django import forms
from management.models import *
from django.core.exceptions import ValidationError
from authentication.models import *
from teacher.models import *

GENDER_CHOICES = (
    ("M", "Male"),
    ("F", "Female")
)

class TeacherProfileForm(forms.Form):
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control select2', 'id': 'gender'}),
        required=True
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'id': 'address'}),
        required=True
    )
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select2', 'id': 'subject', 'data-placeholder': 'Select Subject'}),
        required=True
    )
  
    education = forms.CharField(
        max_length=50, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'education'}),
        required=True
    )

    profile = forms.FileField(
        help_text="Upload image:",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'id': 'profile'}),
        required=False
    )

    def clean_profile(self):
        profile = self.cleaned_data.get('profile')
        if profile and not profile.name.endswith(('.jpg','.jpeg', '.png' )):
            raise forms.ValidationError("Image is not valid")
        return profile