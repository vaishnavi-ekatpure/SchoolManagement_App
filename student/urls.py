from django.urls import path
from . import views

urlpatterns = [
    path('dashboard', views.dashboard, name='student_dashboard'),
    path('student_profile', views.student_profile, name='student_profile'),
    path('teachers', views.teacher_list, name='teachers'),
    path('get_marks', views.get_marks, name='get_marks'),
    path('download_mark_list/<int:id>', views.download_mark_list, name='download_mark_list')
]
