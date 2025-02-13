from django import forms
from django.core.exceptions import ValidationError
from .models import *
from authentication.models import *
from django_select2 import forms as s2forms

class ClassForm(forms.Form):
    class_teach = forms.ModelMultipleChoiceField(
        queryset=Class.objects.none(),  
        widget=s2forms.Select2MultipleWidget(
            attrs={'class': 'form-control select2', 'id': 'class_teach', 'data-placeholder': 'Select classes'}
        ),
        required=True
    )

    def __init__(self, *args, subject=None, **kwargs):
        super().__init__(*args, **kwargs)
        if subject:
            self.fields['class_teach'].queryset = Class.objects.filter(class_subject__icontains = subject.id )
        else:
            self.fields['class_teach'].queryset = Class.objects.none()


class ClassTeacherForm(forms.Form):
    class_teacher = forms.ModelChoiceField(
        queryset=Class.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select2', 'id': 'class_teacher', 'data-placeholder': 'Select classe'}),
        required=True
    )    

class ClassSubjectForm(forms.Form):
    class_subject = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        widget=s2forms.Select2MultipleWidget(
            attrs={'class': 'form-control select2', 'id': 'class_subject', 'data-placeholder': 'Select Subject'}
        ),
        required=True
    )    

