from django.db import models

class Subject(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Class(models.Model):
    class_name = models.CharField(max_length=50, unique=True)
    class_subject = models.JSONField(default=list, null=True)

    def __str__(self):
        return self.class_name
    
    def get_subjects(self):
        subjects = Subject.objects.filter(id__in=self.class_subject)
        return subjects