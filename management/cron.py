from authentication.models import *
from management.models import *
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from io import BytesIO
from xhtml2pdf import pisa  
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def render_to_pdf(template_src, context_dict={}):
    template = render_to_string(template_src, context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(template.encode("ISO-8859-1")), result)
    
    if not pdf.err:
        return result.getvalue()
    return None

def send_email_with_pdf_attachment():
    users = CustomUser.objects.exclude(role=1).all()
    template = 'management/daily_user_list.html'
    context = {
        'users': users,
    }
    pdf_content = render_to_pdf(template, context)
    
    if pdf_content:
        try:
            subject = "Daily Created User List"
            from_email = settings.EMAIL_HOST_USER
            recipient_email = settings.ALTERNATIVE_ADMIN_EMAIL
            email = EmailMessage(subject, "Please find the attached user list.", from_email, [recipient_email])

            todays_date = timezone.now().date()
            
            filename = f"{todays_date}_user_list.pdf"
            email.attach(filename, pdf_content, 'application/pdf')
            
            email.send()
            logger.info(f'Mail send sucessfully')
        except Exception as e:
            logger.info(f'Failed to send email: {e}')
    else:
        logger.info(f'Failed to generate PDF.')