from django.urls import path
from . import views

urlpatterns = [
    path('dashboard', views.dashboard, name='teacher_dashboard'),
    path('teacher_profile', views.teacher_profile, name='teacher_profile'),
    path('student_list', views.student_list, name='student_list_in_teacher'),
    path('get_student_marks/<int:id>/<int:sem>', views.get_student_marks, name='get_student_marks'),
    path('add_marks', views.add_marks, name='add_marks'),
]
