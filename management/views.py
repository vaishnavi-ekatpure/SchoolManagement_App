from django.shortcuts import render,redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from authentication.models import *
from .models import *
from teacher.models import *
from student.models import *
from django.core.mail import send_mail
from django.conf import settings
from .forms import *
from services.mailservice import *
from services.formsservice import *
import string

@login_required(login_url='login')
def dashboard(request):
    users = CustomUser.objects.all()
    active_teacher = users.filter(role=2, is_active=1).count()
    inactive_teacher = users.filter(role=2, is_active=0).count()
    active_student = users.filter(role=3, is_active=1).count()
    inactive_student = users.filter(role=3, is_active=0).count()
    
    return render(request,
                   'dashboard.html',
                    {'active_teacher': active_teacher,
                     'inactive_teacher': inactive_teacher,
                     'active_student': active_student,
                     'inactive_student': inactive_student})

@login_required(login_url='login')
def teacher_list(request):
    teachers = CustomUser.objects.filter(role=2)
    return render(request, 'management/teacher_list.html' , {'teachers':teachers})

@login_required(login_url='login')
def change_status(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        is_active = request.POST.get('is_active')

        try:
            user = CustomUser.objects.get(id=user_id)
            user.is_active = bool(int(is_active))  
            user.save()

            mailer = Mailer(request)
            mailer.change_status_mail(user)
            return JsonResponse({'status': 'success'})
        except CustomUser.DoesNotExist:
            return JsonResponse({'status': 'error'})
    return JsonResponse({'status': 'error'})

@login_required(login_url='login')
def student_list(request):
    students = CustomUser.objects.filter(role=3)
    return render(request, 'management/student_list.html' , {'students':students})

@login_required(login_url='login')
def subject_list(request):
    subjects = Subject.objects.all()
    return render(request, 'management/subject_list.html', {'subjects': subjects})

@login_required(login_url='login')
def create_subject(request):
    if request.method == 'POST':
        subject_name = string.capwords(request.POST.get('subject_name'))

        if subject_name:
            subject_exist = Subject.objects.filter(name=subject_name).exists()
            if subject_exist:
                messages.error(request, "Subject already exist")
                return redirect('subjects_list') 
            
            Subject.objects.create(name=subject_name)
            messages.success(request, "Subject created")
            return redirect('subjects_list') 
        
    return redirect('subjects_list') 

@login_required(login_url='login')
def delete_subject(request):
    if request.method == 'POST':
        subject_id = request.POST.get('subject_id')

        try:
            subject = Subject.objects.get(id=subject_id).delete()
            classes_to_update = Class.objects.filter(class_subject__icontains=subject_id)

            for class_obj in classes_to_update:
                updated_subjects = [sid for sid in class_obj.class_subject if sid != int(subject_id)]
                class_obj.class_subject = updated_subjects  
                class_obj.save()

            return JsonResponse({'status': 'success'})
        except Subject.DoesNotExist:
            return JsonResponse({'status': 'error'})
        
    return JsonResponse({'status': 'error'})

@login_required(login_url='login')
def edit_subject(request, id):
    subject = get_object_or_404(Subject, id=id)

    if request.method == 'GET':
        data = {
            'id': subject.id,
            'name': subject.name,
        }
        return JsonResponse(data)

    elif request.method == 'POST':
        subject_name = string.capwords(request.POST.get('subject_name'))
        subject_exist = Subject.objects.filter(name=subject_name).exclude(id=id).exists()
        
        if subject_exist:
                messages.error(request, "Subject already exist")
                return redirect('subjects_list') 
            
        if subject_name:
            subject.name = subject_name
            subject.save()
            return redirect('subjects_list')
        
    return redirect('subjects_list')  

@login_required(login_url='login')
def get_teacher(request,id):
    try: 
        teacher = CustomUser.objects.get(id=id)
        try:
         teacher_profile = TeacherProfile.objects.get(user=teacher)
        except TeacherProfile.DoesNotExist:
            teacher_profile = None

        subject = teacher_profile.subject if teacher_profile else None
        class_teach = teacher_profile.class_teach if teacher_profile else None
        class_teacher = teacher_profile.class_teacher if teacher_profile else None

        form = ClassForm(subject=subject,initial={
                'class_teach': class_teach,
            })
        
        classTeacherForm = ClassTeacherForm(initial={
                'class_teacher': class_teacher,
            })

        return render(request, 'management/view_teacher.html', {'teacher': teacher, 'teacher_profile': teacher_profile, 'form': form, 'classTeacherForm': classTeacherForm}) 
    except CustomUser.DoesNotExist:
        messages.error(request, 'Teacher not found')
        return redirect('teachers_list')     

@login_required(login_url='login')
def get_student(request,id):
    student = get_object_or_404(CustomUser, id=id)

    try:
        student_profile = StudentProfile.objects.get(user=student)
    except StudentProfile.DoesNotExist:
        student_profile = None

    return render(request, 'management/view_student.html', {'student': student, 'student_profile': student_profile})   

@login_required(login_url='login')
def delete_user(request, id):
    try:
       user = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        user = None   
    if user:
        try:
            return_url = 'teachers_list' if user.role == 2 else 'students_list'
            subject = 'Account Delete'
            message = 'User Account is deleted by admin'
            address = user.email
            send_mail(subject, message, settings.EMAIL_HOST_USER, [address])
            messages.success(request, 'Account deleted successfully')

            user.delete()

            return redirect(return_url)
        except Exception as e:
            print(e)
            messages.error(request, 'Account not delete')
            return redirect(return_url)
    else:
        messages.error(request, 'User not found')
        return redirect('teachers_list')  

@login_required(login_url='login')
def assign_class(request,id):
    if request.method == 'POST':
        classes = request.POST.getlist('class_teach')
        
        if classes:
            teacher_profile = TeacherProfile.objects.get(user=id)
            class_ids = [int(cls) for cls in classes]

            teacher_exist = TeacherProfile.objects.exclude(user=id).filter(subject=teacher_profile.subject.id).first()
            if teacher_exist:
                result = any(item in teacher_exist.class_teach for item in class_ids)
                if result == True:
                    messages.error(request, 'Check class because already teacher is assign')
                    return redirect('get_teacher', id)

            teacher_profile.class_teach = class_ids
            teacher_profile.save()
            
            messages.success(request,'Class added')
            return redirect('get_teacher', id) 
        
        messages.error(request, 'Invalid class')
        return redirect('get_teacher', id) 
    else:
        return redirect('get_teacher', id) 

@login_required(login_url='login')
def admin_profile(request):
    user = request.user

    if request.method == 'POST':
        form = CommonFiledForm(request.POST, user_id=user.id)
        if form.is_valid():
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.username = form.cleaned_data['username']
            user.email = form.cleaned_data['email']
            user.phone_number = form.cleaned_data['phone_number']
            user.save()
            messages.success(request, 'Profile Updated')
            return render(request, 'management/admin_profile.html', {'form': form}) 
    else:
        form = CommonFiledForm(
            initial={
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username,
                'email': user.email,
                'phone_number': user.phone_number,
            },
            user_id=user.id
        )

    return render(request, 'management/admin_profile.html', {'form': form})    

@login_required(login_url='login')
def profile_incomplete_notification(request, id):
    try: 
        teacher = CustomUser.objects.get(id=id)
        mailer = Mailer(request)
        mailer.profile_complete_notify(teacher)

        messages.success(request, 'Mail send successfully')
        return redirect('teachers_list') 
    except CustomUser.DoesNotExist:
        messages.error(request, 'Teacher not found')
        return redirect('teachers_list')  
    
@login_required(login_url='login')
def assign_class_teacher(request, id):
    if request.method == 'POST':
        form = ClassTeacherForm(request.POST)
        
        if form.is_valid():
            teacher_profile = TeacherProfile.objects.get(user=id)
            class_name = form.cleaned_data['class_teacher']

            try:
                is_teacher_exists = TeacherProfile.objects.exclude(user=id).get(class_teacher=class_name)

                messages.error(request, 'Already class has assigned another teacher')
                return redirect('get_teacher', id)
            except TeacherProfile.DoesNotExist:
                teacher_profile.class_teacher = class_name
                teacher_profile.save()

                messages.success(request,'Class Teacher assign')
                return redirect('get_teacher', id) 
        
        messages.error(request, 'Invalid class')
        return redirect('get_teacher', id) 
    else:
        return redirect('get_teacher', id)
    
@login_required(login_url='login')
def remove_class_teacher(request, id):
    try:
        tecaher_profile = TeacherProfile.objects.get(user=id)
        tecaher_profile.class_teacher = None
        tecaher_profile.save()

        messages.success(request, 'Class removed')
        return redirect('get_teacher', id)

    except TeacherProfile.DoesNotExist:
        messages.error(request, 'Teacher details not found')
        return redirect('get_teacher', id)  

@login_required(login_url='login')
def remove_assigned_class(request, user_id, class_id):
    try: 
        teacher_profile = TeacherProfile.objects.get(user=user_id)
        class_teach = teacher_profile.class_teach  
        
        if class_id in class_teach:
            class_teach.remove(class_id)  
            teacher_profile.class_teach = class_teach  
            teacher_profile.save()
            messages.success(request, 'Class removed successfully')
        else:
            messages.error(request, 'Class not found in assigned classes')
        return redirect('get_teacher', user_id)
    except TeacherProfile.DoesNotExist:
        messages.error(request, 'Teacher details not found')     
        return redirect('get_teacher', user_id)
    
@login_required(login_url='login')
def class_list(request):
    classes = Class.objects.all()

    return render(request, 'management/class_list.html', {'classes': classes}) 

# Not used
@login_required(login_url='login')
def get_subject(request, id):
    try:
        class_record = Class.objects.get(id=id)
        initial_subject = class_record.class_subject if class_record else None

        form = ClassSubjectForm(initial={'class_subject': initial_subject})
        
        form_html = render_to_string('management/add_subject_form.html', {'form': form}, request)

        return JsonResponse({'form_html': form_html})
    except Class.DoesNotExist:
        return JsonResponse({'error': 'Class not found'}, status=404)

@login_required(login_url='login')
def add_class_subject(request,id):
    if request.method == 'POST':
        subject_list = request.POST.getlist('class_subject')
        
        if subject_list:
            class_details = Class.objects.get(id=id)
            subject_list = list(map(int, subject_list))
            removed_subject = [ sub for sub in class_details.class_subject if sub not in subject_list ] if class_details.class_subject else []
           
            teacher_list = TeacherProfile.objects.filter(class_teach__icontains=id, subject__in=removed_subject)
            for teacher in teacher_list:
                if id in teacher.class_teach:
                    teacher.class_teach.remove(id)
                    teacher.save()
          

            class_details.class_subject = subject_list
            class_details.save()
            
            messages.success(request,'Subject added')
            return redirect('class_list') 
        
        messages.error(request, 'Invalid Subject')
        return redirect('class_list') 
    else:
        return redirect('class_list')

@login_required(login_url='login')
def remove_class_subject(request, class_id, subject_id):
    try: 
        class_details = Class.objects.get(id=class_id)
        class_subject = class_details.class_subject  
        if subject_id in class_subject:
            class_subject.remove(subject_id)  
            class_details.class_subject = class_subject  
            class_details.save()
            
            teacher_list = TeacherProfile.objects.filter(class_teach__icontains=class_id)

            for teacher in teacher_list:
                updated_subjects = [sid for sid in teacher.class_teach if sid != int(class_id)]
                teacher.class_teach = updated_subjects  
                teacher.save()
            
            messages.success(request, 'Subject removed successfully')
        else:
            messages.error(request, 'Subject not found in assigned classe')
        return redirect('class_list')
    except Class.DoesNotExist:
        messages.error(request, 'Class details not found')     
        return redirect('class_list')       