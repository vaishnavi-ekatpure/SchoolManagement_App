from django import forms
from .models import CustomUser
from django.core.exceptions import ValidationError

ROLE_CHOICES = (
    # (1, 'Admin'),
    (2, 'Teacher'),
    (3, 'Student'),
)

class UserRegistration(forms.Form):
    first_name = forms.CharField(
        min_length=5,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'first_name'})
    )
    last_name = forms.CharField(
        min_length=5,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'last_name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'id': 'email'})
    )
    username = forms.CharField(
        min_length=5,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'username'})
    )
    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'password'})
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control select2', 'id': 'role'})
    )


    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError("A user with this username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email
    

class UserLogin(forms.Form):
    username = forms.CharField(
        min_length=5,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'username'})
    )
    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'password'})
    ) 


class ResetPasswordForm(forms.Form):
    password=forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'password'}))
    confirm_password=forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'confirm_password'}))

    def clean_confirm_password(self):
        cleaned_data = super(ResetPasswordForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
            
        if password != confirm_password:
            raise forms.ValidationError(
                "password and confirm_password does not match"
            )      
