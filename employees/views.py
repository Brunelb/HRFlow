from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied

from .models import Employee
from .forms import EmployeeForm
from accounts.decorators import role_required


@login_required
def employee_list(request):
    user = request.user

    if user.role == 'manager':
        employees = Employee.objects.filter(manager=user)

    elif user.role in ['hr', 'admin']:
        employees = Employee.objects.all()

    else:
        try:
            employees = Employee.objects.filter(pk=user.employee_profile.pk)
        except Employee.DoesNotExist:
            employees = Employee.objects.none()

    return render(request, 'employees/employee_list.html', {
        'employees': employees
    })


@login_required
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    user = request.user

    if user.role == 'employee':
        if not hasattr(user, 'employee_profile') or employee != user.employee_profile:
            raise PermissionDenied

    elif user.role == 'manager':
        if employee.manager != user and employee.user != user:
            raise PermissionDenied

    elif user.role not in ['hr', 'admin']:
        raise PermissionDenied

    return render(request, 'employees/employee_detail.html', {
        'employee': employee
    })


@login_required
@role_required(['hr', 'admin'])
def employee_create(request):
    department_id = request.GET.get('department') or request.POST.get('department')

    if request.method == 'POST':
        form = EmployeeForm(
            request.POST,
            request.FILES,
            department_id=department_id
        )

        if form.is_valid():
            form.save()
            messages.success(request, "La fiche employé a été créée avec succès.")
            return redirect('employee_list')
    else:
        form = EmployeeForm(department_id=department_id)

    return render(request, 'employees/employee_form.html', {
        'form': form,
        'title': 'Créer une fiche employé',
        'selected_department': department_id,
    })


@login_required
@role_required(['hr', 'admin'])
def employee_update(request, pk):
    employee = get_object_or_404(Employee, pk=pk)

    department_id = (
        request.GET.get('department')
        or request.POST.get('department')
        or employee.department_id
    )

    if request.method == 'POST':
        form = EmployeeForm(
            request.POST,
            request.FILES,
            instance=employee,
            department_id=department_id
        )

        if form.is_valid():
            form.save()
            messages.success(request, "La fiche employé a été modifiée avec succès.")
            return redirect('employee_detail', pk=employee.pk)
    else:
        form = EmployeeForm(
            instance=employee,
            department_id=department_id
        )

    return render(request, 'employees/employee_form.html', {
        'form': form,
        'title': 'Modifier une fiche employé',
        'selected_department': department_id,
    })