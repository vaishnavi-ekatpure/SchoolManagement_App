from teacher.models import *
from student.models import *

def user_profile_image(request):
    """
    Returns the profile image URL based on the logged-in user’s role.
    """
    profile_image_url = None
    
    if request.user.is_authenticated:
        user = request.user
        if user.role == 1:  
            profile_image_url = None  
        elif user.role == 2:  
            try:
                teacher_details = TeacherProfile.objects.get(user=user)
                profile_image_url = teacher_details.profile if teacher_details.profile else None
            except TeacherProfile.DoesNotExist:
                profile_image_url = None
        elif user.role == 3:  
            try:
                student_details = StudentProfile.objects.get(user=user)
                profile_image_url = student_details.profile if student_details.profile else None
            except StudentProfile.DoesNotExist:
                profile_image_url = None

    return {'profile_image_url': profile_image_url}
