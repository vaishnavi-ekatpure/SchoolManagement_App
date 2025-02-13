from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register', views.user_registration, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout', views.user_logout, name='logout'),

    path('forgot_password', views.send_email, name='forgot_password'),
    path('reset_password/<token>', views.reset_password, name='reset_password'),
    path('set_password', views.set_password, name='set_password'),

    path("google/login/", views.google_login, name="google_login"),
    path("accounts/google/login/callback/", views.google_callback, name="google_callback"),
    path("google_register/", views.google_register, name="google_register")
]
