from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .forms import *
from .models import *
import uuid
from datetime import datetime, timedelta
from services.mailservice import *
import requests
from urllib.parse import urlencode
from django.utils.crypto import get_random_string
from twilio.rest import Client
import string

def home(request):
    return render(request, 'authentication/home.html')

def user_registration(request):
    if request.method == 'POST':
        form = UserRegistration(request.POST)
        
        if form.is_valid():
            cd = form.cleaned_data
            user = CustomUser.objects.create_user(cd["username"], cd["email"], cd["password"])
            user.first_name = cd["first_name"]
            user.last_name = cd["last_name"]
            user.role = cd["role"]
            user.is_active = 0
            user.save()

            mailer = Mailer(request)
            mailer.user_register_email(user)

            # send_sms(user)
            messages.success(request, "Registration Successfully wait for admin approval")
            return redirect('login')
        
        return render(request, 'authentication/register.html', {'form': form})

    form = UserRegistration()        
    return render (request, 'authentication/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = UserLogin(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            User = get_user_model()
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = None

            if user and user.check_password(password):
                if user.is_active:
                    login(request, user)
                    messages.success(request, 'Login Successfully')
                    return redirect('management_dashboard' if user.role == 1 else 
                                    'teacher_dashboard' if user.role == 2 else 
                                    'student_dashboard')
                else:
                    messages.error(request, "Your account is inactive. Please contact admin.")
                    return render(request, 'authentication/login.html', {'form': form})
            else:
                messages.error(request, "Invalid credentials")
                return render(request, 'authentication/login.html', {'form': form})

    else:
        form = UserLogin()
    
    return render(request, 'authentication/login.html', {'form': form})


@login_required(login_url='login')
def user_logout(request):
    logout(request)
    return redirect('login')

def send_email(request):
    email = request.POST.get('email')
    try:
        user = CustomUser.objects.get(email=email)
        user.password_reset_token = uuid.uuid4()
        user.token_expired_at = datetime.now() + timedelta(minutes = 5)
        user.save()

        mailer = Mailer(request)
        mailer.password_reset_email(user)

        messages.success(request, 'Passowrd reset link is send to your email')
        return redirect('login')
        
    except CustomUser.DoesNotExist:
        messages.error(request, 'Enter valid email')  
        return redirect('login')  
    
def reset_password(request, token):
    form = ResetPasswordForm()
    return render(request, 'authentication/reset_password.html', {'form': form, 'token': token})  

def set_password(request):
    form = ResetPasswordForm(request.POST)
    token = request.POST.get('token')
    if form.is_valid():
        try:
           user = CustomUser.objects.filter(password_reset_token=token).filter(token_expired_at__gte=datetime.now()).get()
           user.set_password(form.cleaned_data['password'])
           user.password_reset_token = None
           user.save()
           messages.success(request, 'Password chnaged successfully')
           return redirect('login')
        except CustomUser.DoesNotExist:
            messages.error(request, 'Invalid token')   
            return redirect('login')

    return render(request, 'authentication/reset_password.html', {'form': form, 'token':token }) 



def google_login(request):
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
    }
    google_auth_url = f"{settings.GOOGLE_AUTH_URI}?{urlencode(params)}"
    
    return redirect(google_auth_url)

def google_callback(request):
    code = request.GET.get("code")
    if not code:
        return redirect("login")  

    token_data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    token_response = requests.post(settings.GOOGLE_TOKEN_URI, data=token_data)
    token_response_data = token_response.json()

    access_token = token_response_data.get("access_token")
    if not access_token:
        return redirect("login")

    user_info_response = requests.get(
        settings.GOOGLE_USER_INFO_URI,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    user_info = user_info_response.json()

    email = user_info.get("email")
    name = user_info.get("name")

    user_exist = CustomUser.objects.filter(email=email).first()
    if not user_exist:
        user_name = name.split(" ") if name else []
        user = {
            'email' : email,
            'first_name' : user_name[0] if user_name else '',
            'last_name' : user_name[1] if user_name else '',
        }
        return render(request, 'authentication/google_register.html', {'user': user})


    if user_exist.is_active:
        login(request, user_exist)
        messages.success(request, 'Login Successfully')
        return redirect('management_dashboard' if user_exist.role == 1 else 
                        'teacher_dashboard' if user_exist.role == 2 else 
                        'student_dashboard')
    else:
        messages.error(request, "Your account is inactive.")
        return redirect('login')
    
def google_register(request):
    data = request.POST
    username = get_random_string(8, allowed_chars=string.ascii_uppercase + string.digits)

    user = CustomUser.objects.create_user(username, data["email"])
    user.first_name = data["first_name"]
    user.last_name = data["last_name"]
    user.role = data["role"]
    user.is_active = 0
    user.save()

    if user:
        mailer = Mailer(request)
        mailer.user_register_email(user)
            
        messages.success(request, "Registration Successfully wait for admin approval")
        return redirect('login')
    else:
        messages.error(request, "Not register")
        return redirect('home')
    

def send_sms(user):
    try:
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        twilio_phone_no = settings.TWILIO_PHONE_NO

        client = Client(account_sid, auth_token)

        recipient_list = CustomUser.objects.filter(is_superuser=1, is_active=1, role=1).values_list('phone_number', flat=True)
        
        if recipient_list:
            message = "New "+ "teacher " if int(user.role)==2 else "student "+"created on SchoolManagement platform please activate there account"
            
            for phone_no in recipient_list:
                client.messages.create(
                    body=message,
                    to="+91"+phone_no, 
                    from_=twilio_phone_no  
                )

    except Exception as e:
        print(f"Error sending user registration sms: {e}")        
    
