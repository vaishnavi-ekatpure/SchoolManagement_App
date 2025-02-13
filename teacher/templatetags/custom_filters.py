from django import template
from management.models import *
register = template.Library()

@register.filter
def get_value(dictionary, key):
    return dictionary.get(str(key), '')  

@register.filter
def get_subject(id):
    subject = Subject.objects.filter(id=id).first()
    return subject

@register.filter
def is_pass(marks):
    if marks and marks >=35:
        return 'PASS'
    else:
        return 'FAIL'
    
@register.filter
def get_percentage(marks_dict):
    if not isinstance(marks_dict, dict):
        return 0  

    marks = [value for value in marks_dict.values() if isinstance(value, (int, float))]  
    if not marks:
        return 0  

    percentage = sum(marks) / len(marks)  
    return percentage 
    
