from django.db import models
from authentication.models import *
from management.models import *

class TeacherProfile(models.Model):
    genderChoice = (
        ("M","Male"),("F","Female")
        )
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)  
    gender = models.CharField(max_length=1,choices=genderChoice)
    address = models.TextField()
    class_teacher = models.ForeignKey(Class, on_delete=models.CASCADE, null=True, blank=True)
    class_teach = models.JSONField(default=list, null=True)
    subject = models.ForeignKey(Subject,on_delete=models.CASCADE, null=True, blank=True)
    education = models.CharField(max_length=10)
    profile = models.ImageField(upload_to='static/teacher_profiles/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def get_class_names(self):
        class_ids = self.class_teach
        class_names = Class.objects.filter(id__in=class_ids)
        return class_names