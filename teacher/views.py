from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import*
from .forms import *
from student.models import *
from services.formsservice import *

@login_required(login_url='login')
def dashboard(request):
    teacher_profile = TeacherProfile.objects.filter(user=request.user.id).first()
    student_mark_list = []

    if teacher_profile and teacher_profile.class_teacher:
        student_mark_list = StudentMarks.objects.filter(student_class=teacher_profile.class_teacher.id).all()

    return render(request, 'dashboard.html', {'teacher_profile': teacher_profile, 'student_mark_list': student_mark_list})

@login_required(login_url='login')
def teacher_profile(request):
    user = request.user
    try:
       teacher_profile = TeacherProfile.objects.get(user=user.id)
    except TeacherProfile.DoesNotExist:
       teacher_profile = None
       
    if request.method == 'POST':
        form = TeacherProfileForm(request.POST, request.FILES)
        common_form = CommonFiledForm(request.POST, user_id=user.id)

        if form.is_valid() and common_form.is_valid():
            cd = form.cleaned_data
            common_form_cd = common_form.cleaned_data

            teacher_profile = teacher_profile if teacher_profile else TeacherProfile()
            teacher_profile.user = request.user
            teacher_profile.subject = cd['subject']
            teacher_profile.gender = cd['gender']
            teacher_profile.address = cd['address']
            teacher_profile.education = cd['education']

            user.first_name = common_form_cd['first_name']
            user.last_name = common_form_cd['last_name']
            user.email = common_form_cd['email']
            user.username = common_form_cd['username']
            user.phone_number = common_form_cd['phone_number']
            user.save()

            if 'profile' in request.FILES:
                teacher_profile.profile = request.FILES['profile']

            teacher_profile.save()

            messages.success(request, "Profile updated")
            return redirect('teacher_dashboard')  
    else:
        common_form = CommonFiledForm(initial= {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'username': user.username,
            'phone_number': user.phone_number,
        }) 
        initial_data = {}

        if teacher_profile:
            initial_data.update({
                'gender': teacher_profile.gender,
                'address': teacher_profile.address,
                'subject': teacher_profile.subject,
                'education': teacher_profile.education
            })

        form = TeacherProfileForm(initial=initial_data ) 

    return render(request, 'teacher/teacher_profile.html', {'form': form, 'common_form': common_form})

@login_required(login_url='login')
def student_list(request):
    teacher = TeacherProfile.objects.filter(user=request.user.id).first()
    if teacher:
        students = StudentProfile.objects.filter(class_taken=teacher.class_teacher, user__role=3)
    else:
        students = None    
   
    return render(request, 'teacher/student_list.html' , {'students':students})

@login_required(login_url='login')
def get_student_marks(request, id,sem):
    teacher_class = request.user.teacherprofile.class_teacher
    subjects = Class.objects.filter(class_name=teacher_class).first()

    student_marks = StudentMarks.objects.filter(semester=sem, student_class=teacher_class,user=id).first()

    return render(request, 'teacher/add_marks.html', {'student_marks': student_marks, 'subjects' : subjects, 'sem': sem, 'id': id})   

@login_required(login_url='login')
def add_marks(request):
        try:
            user_id = request.POST['id']
            sem = request.POST['sem']
            student = StudentProfile.objects.filter(user=user_id).select_related('class_taken').get()
            marks = {}
            teacher_class = request.user.teacherprofile.class_teacher

            for class_id in student.class_taken.class_subject:
                    marks[str(class_id)] = int(request.POST.get(str(class_id), None) )

            student_marks = StudentMarks.objects.filter(user=user_id, semester=sem, student_class=teacher_class).first()
            if not student_marks:
                student_marks = StudentMarks()
                student_marks.user = student.user
                student_marks.semester = sem
                student_marks.marks = marks
                student_marks.student_class = student.class_taken
                student_marks.save()
            else:
                student_marks.marks = marks
                student_marks.save()  
            
            messages.success(request, 'Marks added successfully')
            return redirect('student_list_in_teacher')   
        except Exception as e:
            messages.error(request, 'An error occured')
            return redirect('student_list_in_teacher')