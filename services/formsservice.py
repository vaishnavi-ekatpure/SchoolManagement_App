from django import forms
from management.models import *
from django.core.exceptions import ValidationError
from authentication.models import *

class CommonFiledForm(forms.Form):
    first_name = forms.CharField(
        min_length=5,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'first_name'}),
        required=True
    )
    last_name = forms.CharField(
        min_length=5,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'last_name'}),
        required=True
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'id': 'email'}),
        required=True
    )
    username = forms.CharField(
        min_length=5,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'username'}),
        required=True
    )

    phone_number = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control',  'id': 'phone_number'}),
        required=True
    )

    def __init__(self, *args, **kwargs):
        self.user_id = kwargs.pop('user_id', None)
        super(CommonFiledForm, self).__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exclude(id=self.user_id).exists():
            raise ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exclude(id=self.user_id).exists():
            raise ValidationError("This email is already in use.")
        return email

    def clean_phone_number(self):
        phone_no = self.cleaned_data.get('phone_number')
        if not (phone_no and phone_no.isdigit() and len(phone_no) == 10):
            raise ValidationError('Phone number must be 10 digits long and numeric.')
        if CustomUser.objects.filter(phone_number=phone_no).exclude(id=self.user_id).exists():
            raise ValidationError("This phone number is already in use.")
        return phone_no
   


