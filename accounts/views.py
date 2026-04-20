from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

@login_required
def role_redirect_view(request):
    user = request.user

    if user.role == 'admin':
        return redirect('admin_dashboard')
    elif user.role == 'hr':
        return redirect('hr_dashboard')
    elif user.role == 'manager':
        return redirect('manager_dashboard')
    else:
        return redirect('employee_dashboard')