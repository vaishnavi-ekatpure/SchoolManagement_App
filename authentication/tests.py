from django.test import TestCase, Client
from django.urls import reverse
from .models import *
from .forms import *

class BaseTestSetup(TestCase):
    def setUp(self):
        self.super_user = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@gmail.com',
            password='Admin@123',
            )
        
        self.teacher = CustomUser.objects.create_user(
            username='teacher',
            email='teacher@gmail.com',
            password='Test@123',
            role=2
        )

        self.student = CustomUser.objects.create_superuser(
            username='student',
            email='student@gmail.com',
            password='Test@123',
            role=3
        )

        self.register_url = reverse('register')  
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.forgot_password_url = reverse('forgot_password')
        self.reset_password_url = reverse('reset_password', kwargs={'token': '550e8400-e29b-41d4-a716-446655440000'})

class TestView(BaseTestSetup):
    def test_home(self):
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'authentication/home.html')
        self.assertEqual(response.status_code, 200)

    def test_user_registration(self):
        data = {
            'first_name' : 'student',
            'last_name' : 'student',
            'email' : 'student2@gmail.com',
            'username' : 'student2',
            'password': 'Test@123',
            'role' : 3
        } 

        form = UserRegistration(data)
        self.assertTrue(form.is_valid())
        response = self.client.post(self.register_url, data) 
        self.assertEquals(response.status_code, 302)  
        self.assertRedirects(response, self.login_url) 

    def test_user_login(self):
        data = {
            'username' : self.teacher.username,
            'password' : self.teacher.password
        } 

        form = UserLogin(data)
        self.assertTrue(form.is_valid())
        response = self.client.post(self.login_url, data)
        self.assertEquals(response.status_code, 200) 

    def test_user_logout(self):
        response = self.client.get(self.logout_url)
        self.assertEquals(response.status_code, 302)

    def test_forgot_password(self):
        data = {
            'email' : 'teacher@gmail.com'
        }
        response = self.client.post(self.forgot_password_url, data)
        self.assertEqual(response.status_code, 302) 

    def test_reset_password(self):
        response = self.client.get(self.reset_password_url)  
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/reset_password.html')   

    def test_google_login(self):
        response = self.client.get(reverse('google_login')) 
        self.assertEqual(response.status_code, 302)  
        self.assertTrue('https://accounts.google.com/o/oauth2/auth' in response.url)