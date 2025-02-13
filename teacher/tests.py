from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages 
from authentication.models import *
from student.models import *
from management.models import *
from .models import *
from .forms import *

class BaseTestSetup(TestCase):
    def setUp(self):
        self.class_name = Class.objects.create(class_name='First Standard')
        self.subject = Subject.objects.create(name='Math')
        self.user = CustomUser.objects.create_user(
            username = 'teacher',
            first_name = 'teacher',
            last_name = 'teacher',
            email = 'teacher@gmail.com',
            password = 'Test@123',
            role = 2
        )

        self.student = CustomUser.objects.create_user(
            username = 'student',
            first_name = 'student',
            last_name = 'student',
            email = 'student@gmail.com',
            password = 'Test@123',
            role = 3
        )

        self.teacher_profile = TeacherProfile.objects.create(
            user = self.user,
            gender = "M",
            address = "Mumbai",
            subject = self.subject,
            education = 'M.com',
            class_teacher = self.class_name
        )

        self.student_profile = StudentProfile.objects.create(
            user=self.student,
            date_of_birth='2000-01-01',
            gender='M',
            address='Pune',
            class_taken=self.class_name
        )

    def login_user(self):
        # Helper function to log in the user
        response = self.client.post(reverse('login'), {
            'username': 'teacher',
            'password': 'Test@123'
        })
        self.assertRedirects(response, '/teacher/dashboard', status_code=302,  target_status_code=200, fetch_redirect_response=True)

class TestViews(BaseTestSetup):
    def test_dashboard(self):
        self.login_user()

        response = self.client.get(reverse('teacher_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertIn('teacher_profile', response.context) 

    def test_teacher_profile(self):
        self.login_user()

        response = self.client.get(reverse('teacher_profile')) 
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'teacher/teacher_profile.html')
        self.assertIn('form', response.context)  

    def test_teacher_profile_post(self):
        self.login_user()

        data = {
            'gender' : 'M',
            'address' : 'Pune',
            'subject' : self.subject.id,
            'phone_number' : '8765434567',
            'education' : 'B.S.C',
            'first_name': 'teacher',
            'last_name': 'teacher',
            'email': 'teacher@gmail.com',
            'username': 'teacher',
            'phone_number': '9656545676'
        } 

        response = self.client.post(reverse('teacher_profile'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('teacher_dashboard'))

        teacher_details = TeacherProfile.objects.get(user=self.user)
        self.assertEqual(teacher_details.gender, data['gender'])
        self.assertEqual(teacher_details.address, data['address'])
        self.assertEqual(teacher_details.subject, self.subject)
        self.assertEqual(teacher_details.user.phone_number, data['phone_number'])            
        self.assertEqual(teacher_details.education, data['education'])   


    def test_student_list(self):
        self.login_user()

        response = self.client.get(reverse('student_list_in_teacher'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'teacher/student_list.html')
        self.assertIn('students', response.context) 

    def test_get_student_marks(self):
        self.login_user()

        url = reverse('get_student_marks', args=(self.student.id, 1))  
        response = self.client.get(path=url) 
        variables = {'student_marks', 'subjects', 'sem', 'id'}

        self.assertEqual(response.status_code, 200)  
        self.assertTemplateUsed(response, 'teacher/add_marks.html')        
        self.assertTrue(all(var in response.context for var in variables))

    def test_add_marks(self):
        self.login_user()

        data = {
            "sem" : 1,
            "id" : self.student.id,
            self.subject : 88
        } 

        response = self.client.post(reverse('add_marks'), data) 
        all_messages = [msg for msg in get_messages(response.wsgi_request)]
        
        self.assertTrue(all_messages[0].tags, 'success')
        self.assertEqual(all_messages[0].message, 'Marks added successfully')
        self.assertRedirects(response, reverse('student_list_in_teacher')) 
        self.assertEqual(response.status_code, 302)