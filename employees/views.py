from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Employee
from .forms import EmployeeForm
from accounts.decorators import role_required

@login_required
@role_required(['admin', 'hr', 'manager'])
def employee_list(request):
    if request.user.role == 'manager':
        employees = Employee.objects.select_related('user', 'department', 'manager').filter(manager=request.user)
    else:
        employees = Employee.objects.select_related('user', 'department', 'manager').all()

    return render(request, 'employees/employee_list.html', {'employees': employees})

@login_required
@role_required(['admin', 'hr', 'manager', 'employee'])
def employee_detail(request, pk):
    employee = get_object_or_404(Employee.objects.select_related('user', 'department', 'manager'), pk=pk)

    if request.user.role == 'employee' and employee.user != request.user:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied

    if request.user.role == 'manager' and employee.manager != request.user:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied

    return render(request, 'employees/employee_detail.html', {'employee': employee})

@login_required
@role_required(['admin', 'hr'])
def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('employee_list')
    else:
        form = EmployeeForm()

    return render(request, 'employees/employee_form.html', {'form': form, 'title': 'Créer un employé'})

@login_required
@role_required(['admin', 'hr'])
def employee_update(request, pk):
    employee = get_object_or_404(Employee, pk=pk)

    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('employee_detail', pk=employee.pk)
    else:
        form = EmployeeForm(instance=employee)

    return render(request, 'employees/employee_form.html', {'form': form, 'title': 'Modifier un employé'})