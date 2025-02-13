from django.test import TestCase
from django.urls import reverse
from management.models import *
from .models import *
from .forms import *

class BaseTestSetup(TestCase):
    def setUp(self):
        self.class_name = Class.objects.create(class_name='First Standard')

        self.subject1 = Subject.objects.create(name='English2')
        self.subject2 = Subject.objects.create(name='Marathi')

        self.student = CustomUser.objects.create_user(
            username='student',
            first_name='student',
            last_name='student',
            email='student@gmail.com',
            password='Test@123',
            role=3
        )
        self.student_profile = StudentProfile.objects.create(
            user=self.student,
            date_of_birth='2000-01-01',
            gender='M',
            address='Pune',
            class_taken=self.class_name
        )

        self.student_marks = StudentMarks.objects.create(
            user= self.student,
            student_class=self.class_name,
            semester=1,
            marks={'1':80,'2':90}
        )

    def login_user(self):
        # Helper function to log in the user
        response = self.client.post(reverse('login'), {
            'username': 'student',
            'password': 'Test@123'
        })
       
        self.assertRedirects(response, '/student/dashboard', status_code=302,  target_status_code=200, fetch_redirect_response=True)

class TestViews(BaseTestSetup):
    def test_dashboard(self):
        self.login_user()
        response = self.client.get(reverse('student_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertIn('student_profile', response.context)

    def test_student_profile_get(self):
        self.login_user()
        response = self.client.get(reverse('student_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student/student_profile.html')
        self.assertIn('form', response.context)

    def test_student_profile_post(self):
        self.login_user()
        data = {
            'date_of_birth': '2000-01-01',
            'gender': 'F',
            'address': 'Mumbai',
            'class_taken': self.class_name.id,
            'first_name': 'student',
            'last_name': 'student',
            'email': 'student@gmail.com',
            'username': 'student',
            'phone_number': 9656545676
        }
        response = self.client.post(reverse('student_profile'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('student_dashboard'))

        student_details = StudentProfile.objects.get(user=self.student)
        self.assertEqual(student_details.date_of_birth.strftime('%Y-%m-%d'), data['date_of_birth'])
        self.assertEqual(student_details.gender, data['gender'])
        self.assertEqual(student_details.address, data['address'])
        self.assertEqual(student_details.class_taken, self.class_name)

    def test_student_list(self):
        self.login_user()
        response = self.client.get(reverse('teachers'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student/teacher_list.html')
        self.assertIn('teacher_list', response.context)

    def test_get_marks(self):
        self.login_user()
        response = self.client.get(reverse('get_marks')) 
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student/mark_details.html')
        self.assertIn('marks_records', response.context)

    def test_download_mark_list_view(self):
        self.login_user()
        url = reverse("download_mark_list", args=(self.student_marks.id,))  

        response = self.client.get(path=url)  
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get('Content-Disposition'),
            f"inline; filename={self.student.username}_marks_report.pdf"
        )

    def test_download_mark_list_download(self):
        self.login_user()
        url = reverse('download_mark_list', kwargs={'id': self.student_marks.id})
        
        response = self.client.get(f"{url}?download=1")
        
        expected_filename = f"{self.student.username}_marks_report.pdf"
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get('Content-Disposition'),
            f"attachment; filename={expected_filename}"
        )