import random
from django.core.management.base import BaseCommand
from faker import Faker
from authentication.models import CustomUser  

class Command(BaseCommand):
    help = 'Seed users for CustomUser model'

    def handle(self, *args, **kwargs):
        fake = Faker()

        for _ in range(2):  
            user = CustomUser.objects.create_user(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                username=fake.user_name(),
                role=random.choice([2, 3]),  
                password='Test@123'  
            )
            
            self.stdout.write(f'Successfully created user {user.username} with role {user.role}')
