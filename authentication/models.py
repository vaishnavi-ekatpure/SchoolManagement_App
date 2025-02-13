from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.core.validators import RegexValidator

class CustomManager(UserManager):
    def get_active(self):
        return super().get_queryset().filter(is_active=True)

    def get_inactive(self):
        return super().get_queryset().filter(is_active=False) 

class CustomUser(AbstractUser):
    ROLE = (
        (1, 'Admin'),
        (2, 'Teacher'),
        (3, 'Student'),
    )

    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    
    role = models.IntegerField(choices=ROLE, default=1)
    phone_number = models.CharField(validators=[phone_regex], max_length=10, blank=True, null=True)
    password_reset_token = models.CharField(max_length=200,default=None, blank=True, null=True)
    token_expired_at = models.DateTimeField(default=None, blank=True, null=True)
    # objects = CustomManager()

   
