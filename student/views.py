from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from xhtml2pdf import pisa
from io import BytesIO
from django.template.loader import get_template
from .models import *
from .forms import *
from teacher.models import *
from services.formsservice import *

@login_required(login_url='login')
def dashboard(request):
    student_profile = StudentProfile.objects.filter(user=request.user.id).exists()
    return render(request, 'dashboard.html', {'student_profile': student_profile})

@login_required(login_url='login')
def student_profile(request):
    try:
       student_profile = StudentProfile.objects.get(user=request.user.id)
    except StudentProfile.DoesNotExist:
       student_profile = None
   
    user = request.user   
    if request.method == 'POST':
        form = StudentProfileForm(request.POST,  request.FILES)
        common_form = CommonFiledForm(request.POST,user_id=user.id )
        
        if form.is_valid() and common_form.is_valid():
            cd = form.cleaned_data
            common_cd = common_form.cleaned_data
            
            student_profile = student_profile if student_profile else StudentProfile()
            student_profile.user = request.user
            student_profile.date_of_birth = cd['date_of_birth']
            student_profile.gender = cd['gender']
            student_profile.address = cd['address']
            student_profile.class_taken = cd['class_taken']

            user.first_name = common_cd['first_name']
            user.last_name = common_cd['last_name']
            user.email = common_cd['email']
            user.username = common_cd['username']
            user.phone_number = common_cd['phone_number']
            user.save()

            if 'profile' in request.FILES:
                student_profile.profile = request.FILES['profile']
                
            student_profile.save()

            messages.success(request, "Profile updated")
            return redirect('student_dashboard')  
    else:
        common_form = CommonFiledForm(initial={
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'username': user.username,
            'phone_number': user.phone_number,
        })

        initial_data = {}
        if student_profile:
            initial_data.update({
                'date_of_birth': student_profile.date_of_birth,
                'gender': student_profile.gender,
                'address': student_profile.address,
                'class_taken': student_profile.class_taken,
            })

        form = StudentProfileForm(initial=initial_data)

    return render(request, 'student/student_profile.html', {'form': form, 'common_form': common_form})

@login_required(login_url='login')
def teacher_list(request):
    try:
        class_id = request.user.studentprofile.class_taken.id
    except StudentProfile.DoesNotExist:
        class_id = []   

    teacher_list = TeacherProfile.objects.filter(class_teach__icontains=class_id)
    return render(request, 'student/teacher_list.html' , {'teacher_list': teacher_list})

@login_required(login_url='login')
def get_marks(request):
    marks_records = StudentMarks.objects.filter(user=request.user)
    return render(request,'student/mark_details.html', {'marks_records': marks_records})

@login_required(login_url='login')
def download_mark_list(request, id):
    template = 'student/marks_report.html'
    
    mark_details = StudentMarks.objects.filter(id=id).first()
    name = request.user.first_name
    
    context = {
        'name': name,  
        'marks_record': mark_details if mark_details else None
    }
    pdf = render_to_pdf(template, context)
    
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"{name}_marks_report.pdf"
        
        content = "inline; filename=%s" % filename
        download = request.GET.get("download")
        if download:
            content = "attachment; filename=%s" % filename
        response['Content-Disposition'] = content
        
        return response

    return HttpResponse("Not found", status=404)

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
   
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None