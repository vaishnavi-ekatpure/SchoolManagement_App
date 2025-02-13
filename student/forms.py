from django import forms
from django.core.exceptions import ValidationError
from .models import *

GENDER_CHOICES = (
    ("M", "Male"),
    ("F", "Female")
)

class StudentProfileForm(forms.Form):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'date_of_birth'}),
        required=True
    )
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control select2', 'id': 'gender'}),
        required=True
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'id': 'address'}),
        required=True
    )
    class_taken = forms.ModelChoiceField(
        queryset=Class.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select2', 'id': 'class_taken', 'data-placeholder': 'Select Class'}),
        required=True
    )

    profile = forms.FileField(
        help_text="Upload image:",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'id': 'profile'}),
        required=False
    )

    def clean_profile(self):
        profile = self.cleaned_data.get('profile')
        if profile and not profile.name.endswith(('.jpg','.jpeg','.png' )):
            raise forms.ValidationError("Image is not valid")
        return profile
  