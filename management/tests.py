from django.test import TestCase
from django.urls import reverse
from .models import *
from .forms import *
from teacher.models import *
from authentication.models import *
from django.contrib.messages import get_messages 

class BaseTestSetup(TestCase):
    def setUp(self):
        self.subject_1 = Subject.objects.create(name='test')
        self.subject_math = Subject.objects.create(name='Math')
        self.subject_marathi = Subject.objects.create(name='Marathi')
        self.subject_hindi = Subject.objects.create(name='Hindi')

        self.class_object = Class.objects.create(class_name='First Standard',
                                                 class_subject=[self.subject_math.id]) 

        self.admin_user = CustomUser.objects.create_superuser(
          username='admin',
          password='Admin@123',
          first_name = 'admin',
          last_name = 'admin',
          email = 'admin@gmail.com'
       )

        self.teacher = CustomUser.objects.create_user(
            username = 'teacher',
            first_name = 'teacher',
            last_name = 'teacher',
            email = 'teacher@gmail.com',
            password = 'Test@123',
            phone_number = 9898989898,
            role = 2
        )

        self.teacher_2 = CustomUser.objects.create_user(
            username = 'teacher2',
            first_name = 'teacher2',
            last_name = 'teacher2',
            email = 'teacher2@gmail.com',
            password = 'Test@123',
            phone_number = 9898989895,
            role = 2
        )
      
        self.subject = Subject.objects.create(
          name= 'English'
        )
      
        self.teacher_profile = TeacherProfile.objects.create(
          user = self.teacher,
          gender = 'M',
          address = 'Pune',
          subject = self.subject,
          education = 'B.Com',
          class_teach = [self.class_object.id]
        )

        self.teacher_profile_2 = TeacherProfile.objects.create(
          user = self.teacher_2,
          gender = 'M',
          address = 'Pune',
          subject = self.subject,
          education = 'B.Com',
        )
      
        self.student = CustomUser.objects.create_user(
            username = 'student',
            first_name = 'student',
            last_name = 'student',
            email = 'student@gmail.com',
            password = 'Test@123',
            role = 3
        )

    def login_user(self):
        data = {
            'username': 'admin',
            'password' : 'Admin@123'
        }
        login_response = self.client.post(reverse('login'), data)  
        self.assertRedirects(login_response, '/management/dashboard', status_code=302,  target_status_code=200, fetch_redirect_response=True)

class TestViews(BaseTestSetup):
    def test_dashboard(self):
        self.login_user()
        
        dashboard_response = self.client.get(reverse('management_dashboard'))
        self.assertEqual(dashboard_response.status_code, 200)
        self.assertTemplateUsed(dashboard_response, 'dashboard.html')

        variables = {'active_teacher', 'inactive_teacher', 'active_student', 'inactive_student'}
        self.assertTrue(all(var in dashboard_response.context for var in variables))

    def test_teacher_list(self):
        self.login_user()

        response = self.client.get(reverse('teachers_list')) 
        self.assertEqual(response.status_code, 200) 
        self.assertTemplateUsed(response, 'management/teacher_list.html')   
        self.assertIn('teachers', response.context)  

    def test_change_status(self):
        self.login_user()
        data = {
            'user_id': self.teacher.id,
            'is_active':1
        }

        response = self.client.post(reverse('change_status'), data) 
        self.assertEqual(response.status_code, 200) 
        self.assertJSONEqual(response.content, {'status': 'success'})   

    def test_student_list(self):
        self.login_user()

        response = self.client.get(reverse('students_list')) 
        self.assertEqual(response.status_code, 200) 
        self.assertTemplateUsed(response, 'management/student_list.html')   
        self.assertIn('students', response.context)   

    def test_subject_list(self):
        self.login_user()

        response = self.client.get(reverse('subjects_list')) 
        self.assertEqual(response.status_code, 200) 
        self.assertTemplateUsed(response, 'management/subject_list.html')   
        self.assertIn('subjects', response.context)  

    def test_create_subject(self):
        data = {
            'name' : 'Marathi'
        }
        
        response = self.client.post(reverse('create_subject'), data) 
        self.assertEqual(response.status_code, 302)       

    def test_delete_subject(self):
        self.login_user()
        data = {
            'subject_id' : self.subject.id
        }

        response = self.client.post(reverse('delete_subject'), data)
        self.assertJSONEqual(response.content, {'status': 'success'})
        self.assertEqual(response.status_code, 200)


    def test_edit_subject_with_get(self):
        self.login_user() 
        url = reverse("subject_edit", args=(self.subject.id,))
        response = self.client.get(path=url)
        
        expected_data = {
            'id' : self.subject.id,
            'name' : self.subject.name
        }

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content,expected_data)

    def test_edit_subject_with_post(self):
        self.login_user()
        url = reverse("subject_edit", args=(self.subject.id,))
        data = {
            'subject_name' : 'Mathematics'
        }
        response = self.client.post(path=url, data=data)
        self.subject.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('subjects_list'))
        self.assertEqual(self.subject.name, data['subject_name'])

    def test_get_student(self):
        self.login_user()
        url = reverse("get_student", args=(self.student.id,))    
        
        response = self.client.get(path=url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'management/view_student.html')

    def test_get_teacher_success(self):
        self.login_user()
        url = reverse("get_teacher", args=(self.teacher.id,))  

        response = self.client.get(path=url) 
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'management/view_teacher.html') 

    def test_get_teacher_fail(self):
        self.login_user()  
        url = reverse("get_teacher", args=(10,))  

        response = self.client.get(path=url) 
        self.assertEqual(response.status_code, 302)  
        self.assertRedirects(response, reverse('teachers_list'))

    def test_delete_user_fail(self):
        self.login_user()
        url = reverse("delete_user", args=(10,))  

        response = self.client.get(path=url)
        all_messages = [msg for msg in get_messages(response.wsgi_request)]
        self.assertTrue(all_messages[0].tags, 'error')
        self.assertEqual(all_messages[0].message, 'User not found')
        self.assertRedirects(response, reverse('teachers_list'))

    def test_delete_user_teacher(self):
        self.login_user()
        url = reverse("delete_user", args=(self.teacher.id,))  

        response = self.client.get(path=url) 
        all_messages = [msg for msg in get_messages(response.wsgi_request)] 
       
        self.assertTrue(all_messages[0].tags, 'success')
        self.assertEqual(all_messages[0].message, 'Account deleted successfully')
        self.assertRedirects(response, reverse('teachers_list'))

    def test_delete_user_student(self):  
        self.login_user()
        url = reverse("delete_user", args=(self.student.id,))  

        response = self.client.get(path=url) 
        all_messages = [msg for msg in get_messages(response.wsgi_request)] 

        self.assertTrue(all_messages[0].tags, 'success')
        self.assertEqual(all_messages[0].message, 'Account deleted successfully')
        self.assertRedirects(response, reverse('students_list'))  

        
    def test_assign_class(self):
        self.login_user()  
        data = {
            'class_teach' : self.class_object.id
        }  
        url = reverse("assign_class", args=(self.teacher.id,))
        response = self.client.post(path=url, data=data)
        all_messages = [msg for msg in get_messages(response.wsgi_request)] 

        self.assertTrue(all_messages[0].tags, 'success')
        self.assertEqual(all_messages[0].message, 'Class added')
        self.assertRedirects(response, reverse("get_teacher", args=(self.teacher.id,))) 

    def test_admin_profile(self):
        self.login_user()  
        data = {
            'first_name' : 'admin',
            'last_name' : 'admin',
            'username' : self.admin_user.username,
            'email' : self.admin_user.email,
            'phone_number': '9876545676'
        }  
        response = self.client.post(reverse('admin_profile'), data=data)
        all_messages = [msg for msg in get_messages(response.wsgi_request)] 

        self.assertTrue(all_messages[0].tags, 'success')
        self.assertEqual(all_messages[0].message, 'Profile Updated')
        self.assertTemplateUsed(response, 'management/admin_profile.html')

    def test_profile_incomplete_notification(self):
        self.login_user()
        url = reverse("profile_complete_notify", args=(self.teacher.id,))  
        response = self.client.get(path=url)  
        
        all_messages = [msg for msg in get_messages(response.wsgi_request)] 
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(all_messages[0].tags, 'success')
        self.assertEqual(all_messages[0].message, 'Mail send successfully')
        self.assertRedirects(response, reverse('teachers_list'))  

    def test_assign_class_teacher(self):
        self.login_user()  
        data = {
            'class_teacher': self.class_object.id
        } 
        
        url = reverse("assign_class_teacher", args=(self.teacher.id,))
        response = self.client.post(path=url, data=data)
        all_messages = [msg for msg in get_messages(response.wsgi_request)] 
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(all_messages[0].tags, 'success')
        self.assertEqual(all_messages[0].message, 'Class Teacher assign')
        self.assertRedirects(response, reverse("get_teacher", args=(self.teacher.id,))) 

    def test_remove_class_teacher(self):
        self.login_user()  
        url = reverse("remove_class_teacher", args=(self.teacher.id,))  

        response = self.client.get(path=url)
        all_messages = [msg for msg in get_messages(response.wsgi_request)]
        self.assertTrue(all_messages[0].tags, 'success')
        self.assertEqual(all_messages[0].message, 'Class removed')
        self.assertRedirects(response, reverse("get_teacher", args=(self.teacher.id,)))  

    def test_remove_assigned_class(self):
        self.login_user()  
        url = reverse('remove_assigned_class', args=(self.teacher.id,self.class_object.id)) 

        response = self.client.get(path=url) 
        all_messages = [msg for msg in get_messages(response.wsgi_request)]

        self.assertEqual(response.status_code, 302)
        self.assertTrue(all_messages[0].tags, 'success')
        self.assertEqual(all_messages[0].message, 'Class removed successfully')
        self.assertRedirects(response, reverse("get_teacher", args=(self.teacher.id,)))  

    def test_remove_assigned_class_fail(self):
        self.login_user()  
        url = reverse('remove_assigned_class', args=(self.teacher_2.id,self.class_object.id)) 

        response = self.client.get(path=url) 
        all_messages = [msg for msg in get_messages(response.wsgi_request)]
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(all_messages[0].tags, 'error')
        self.assertEqual(all_messages[0].message, 'Class not found in assigned classes')
        self.assertRedirects(response, reverse("get_teacher", args=(self.teacher_2.id,)))      

    def test_class_list(self):
        self.login_user()
        response = self.client.get(reverse('class_list'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'management/class_list.html')
        self.assertIn('classes', response.context)

    def test_get_subject(self):
        self.login_user()
        url = reverse('get_subject', args=(self.class_object.id,))
        response = self.client.get(path=url) 

        self.assertEqual(response.status_code, 200)

    def test_add_class_subject(self):
        self.login_user()  
        data = {
            'class_subject': [self.subject_hindi.id]
        } 
        
        url = reverse("add_class_subject", args=(self.class_object.id,))
        response = self.client.post(path=url, data=data)
        all_messages = [msg for msg in get_messages(response.wsgi_request)] 
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(all_messages[0].tags, 'success')
        self.assertEqual(all_messages[0].message, 'Subject added')
        self.assertRedirects(response, reverse('class_list'))   

    def test_remove_class_subject(self):
        self.login_user()  
        url = reverse('remove_class_subject', args=(self.class_object.id,self.subject_math.id)) 

        response = self.client.get(path=url) 
        all_messages = [msg for msg in get_messages(response.wsgi_request)]
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(all_messages[0].tags, 'success')
        self.assertEqual(all_messages[0].message, 'Subject removed successfully')
        self.assertRedirects(response, reverse('class_list'))  