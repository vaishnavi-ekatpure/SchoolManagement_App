from django.db import models
from authentication.models import *
from management.models import *

class StudentProfile(models.Model):
    genderChoice = (
        ("M","Male"),("F","Female")
        )
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)  
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1,choices=genderChoice)
    address = models.TextField()
    class_taken = models.ForeignKey(Class, on_delete=models.CASCADE)
    profile = models.ImageField(upload_to='static/student_profiles/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class StudentMarks(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    student_class = models.ForeignKey(Class, on_delete=models.CASCADE)
    semester = models.IntegerField()
    marks = models.JSONField(null=True)

   