from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from accounts.decorators import role_required

@login_required
@role_required(['admin'])
def admin_dashboard(request):
    return render(request, 'dashboard/admin_dashboard.html')

@login_required
@role_required(['hr'])
def hr_dashboard(request):
    return render(request, 'dashboard/hr_dashboard.html')

@login_required
@role_required(['manager'])
def manager_dashboard(request):
    return render(request, 'dashboard/manager_dashboard.html')

@login_required
@role_required(['employee'])
def employee_dashboard(request):
    return render(request, 'dashboard/employee_dashboard.html')