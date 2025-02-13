from django.shortcuts import redirect
from django.contrib import messages

class CheckIsAdminMiddleware:
   def __init__(self, get_response):
       self.get_response = get_response

   def __call__(self, request):
    
       if request.user.is_authenticated:
           role = request.user.role
           path = request.path
           if path.startswith('/management/') and role != 1:
               messages.error(request, "You can't access this URL.")
               return redirect('login')
           elif path.startswith('/teacher/') and role != 2:
               messages.error(request, "You can't access this URL.")
               return redirect('login')
           elif path.startswith('/student/') and role != 3:
               messages.error(request, "You can't access this URL.")
               return redirect('login')
          

       response = self.get_response(request)
       return response