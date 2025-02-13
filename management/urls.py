from django.urls import path
from . import views

urlpatterns = [
    path('dashboard', views.dashboard, name='management_dashboard'),
    path('teachers', views.teacher_list, name='teachers_list'),
    path('teacher/<int:id>', views.get_teacher, name='get_teacher'),
    path('students', views.student_list, name='students_list'),
    path('student/<int:id>', views.get_student, name='get_student'),
    path('change_status/', views.change_status, name='change_status'),
    path('subjects', views.subject_list, name='subjects_list'),
    path('create-subject/', views.create_subject, name='create_subject'),
    path('delete_subject/', views.delete_subject, name='delete_subject'),
    path('subject_edit/<int:id>/', views.edit_subject, name='subject_edit'),

    path('delete_user/<int:id>', views.delete_user, name='delete_user'),
    path('assign_class/<int:id>', views.assign_class, name='assign_class'),

    path('admin_profile', views.admin_profile, name='admin_profile'),

    path('profile_complete_notify/<int:id>/', views.profile_incomplete_notification, name='profile_complete_notify'),
    path('assign_class_teacher/<int:id>', views.assign_class_teacher, name='assign_class_teacher'),
    path('remove_class_teacher/<int:id>', views.remove_class_teacher, name='remove_class_teacher'),

    path('remove_assigned_class/<int:user_id>/<int:class_id>', views.remove_assigned_class, name='remove_assigned_class'),

    path('classes', views.class_list, name='class_list'),
    path('get_subject/<int:id>', views.get_subject, name='get_subject'),
    path('add_class_subject/<int:id>', views.add_class_subject, name='add_class_subject'),
    path('remove_class_subject/<int:class_id>/<int:subject_id>', views.remove_class_subject, name='remove_class_subject'),
]

