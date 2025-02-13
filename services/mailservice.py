from django.template.loader import render_to_string 
from django.core.mail import EmailMessage
from django.conf import settings
from authentication.models import *

class Mailer:

    def __init__(self, request):
        protocol = 'https' if request.is_secure() else 'http'
        domain = request.get_host()
        self.base_url = f"{protocol+':'+domain}"
    
    def password_reset_email(self, user):
        try:
            html_template = 'authentication/emails/password_reset_email.html'
            link = f"{self.base_url+'/reset_password/'+str(user.password_reset_token)}"
            context = {
                'link': link,
                'user_name': user.first_name
            }

            html_message = render_to_string(html_template, { 'context': context })
            subject = 'Password Reset'
            from_email = settings.EMAIL_HOST_USER
            to_email = user.email

            message = EmailMessage(subject, html_message, from_email, [to_email])
            message.content_subtype = 'html'
            message.send()
        except Exception as e:
            print(f"Error sending password reset email: {e}")

    def user_register_email(self, user):
        try:
            link = f"{self.base_url+'/login'}"
            html_template = 'authentication/emails/user_register_email.html'
            
            context = {
                'link': link,
                'user_name': user.first_name
            }
            html_message = render_to_string(html_template, { 'context': context })
            subject = 'New User Register'
            from_email = settings.EMAIL_HOST_USER

            recipient_list = []
            recipient_list = CustomUser.objects.filter(is_superuser=1, is_active=1, role=1).values_list('email', flat=True)

            if not recipient_list:
                 recipient_list.append(settings.ALTERNATIVE_ADMIN_EMAIL)   
            
            message = EmailMessage(subject, html_message, from_email, recipient_list)
            message.content_subtype = 'html'
            message.send()
        except Exception as e:
            print(f"Error sending user registration email: {e}")

    def change_status_mail(self, user):
        try:
            html_template = 'management/emails/account_status_email.html'
            link = f"{self.base_url+'/login'}"
            context = {
                'link': link,
                'user': user
            }

            html_message = render_to_string(html_template, { 'context': context })
            subject = 'Account Status Changed'
            from_email = settings.EMAIL_HOST_USER
            to_email = user.email

            message = EmailMessage(subject, html_message, from_email, [to_email])
            message.content_subtype = 'html'
            message.send()
        except Exception as e:
            print(f"Error sending email: {e}")

    def profile_complete_notify(self, user):
        try:
            html_template = 'management/emails/profile_complete_notify.html'
            context = {
                'user' : user
            }

            html_message = render_to_string(html_template, { 'context': context })
            subject = 'Complete Your Profile'
            from_email = settings.EMAIL_HOST_USER
            to_email = user.email

            message = EmailMessage(subject, html_message, from_email, [to_email])
            message.content_subtype = 'html'
            message.send()
        except Exception as e:
            print(f"Error sending email: {e}")