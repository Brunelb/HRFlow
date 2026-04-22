from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied

from .models import Attendance
from .forms import AttendanceCheckInOutForm, AttendanceAdminForm
from employees.models import Employee
from accounts.decorators import role_required


@login_required
def attendance_list(request):
    user = request.user

    if user.role == 'employee':
        try:
            employee = user.employee_profile
            attendances = Attendance.objects.filter(employee=employee)
        except Employee.DoesNotExist:
            attendances = Attendance.objects.none()

    elif user.role == 'manager':
        attendances = Attendance.objects.filter(employee__manager=user)

    elif user.role in ['hr', 'admin']:
        attendances = Attendance.objects.all()

    else:
        attendances = Attendance.objects.none()

    return render(request, 'attendance/attendance_list.html', {
        'attendances': attendances
    })


@login_required
@role_required(['employee', 'manager', 'hr'])
def attendance_create(request):
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        raise PermissionDenied("Aucune fiche employé liée à ce compte.")

    if request.method == 'POST':
        form = AttendanceCheckInOutForm(request.POST)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.employee = employee
            attendance.save()
            return redirect('attendance_list')
    else:
        form = AttendanceCheckInOutForm()

    return render(request, 'attendance/attendance_form.html', {
        'form': form,
        'title': 'Enregistrer une présence'
    })


@login_required
def attendance_detail(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    user = request.user

    if user.role == 'employee':
        if not hasattr(user, 'employee_profile') or attendance.employee != user.employee_profile:
            raise PermissionDenied

    elif user.role == 'manager':
        if attendance.employee.manager != user:
            raise PermissionDenied

    elif user.role not in ['hr', 'admin']:
        raise PermissionDenied

    return render(request, 'attendance/attendance_detail.html', {
        'attendance': attendance
    })

@login_required
@role_required(['hr', 'admin'])
def attendance_admin_create(request):
    if request.method == 'POST':
        form = AttendanceAdminForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('attendance_list')
    else:
        form = AttendanceAdminForm()

    return render(request, 'attendance/attendance_form.html', {
        'form': form,
        'title': 'Ajouter une présence (RH/Admin)'
    })

@login_required
@role_required(['hr', 'admin'])
def attendance_update(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)

    if request.method == 'POST':
        form = AttendanceAdminForm(request.POST, instance=attendance)
        if form.is_valid():
            form.save()
            return redirect('attendance_detail', pk=attendance.pk)
    else:
        form = AttendanceAdminForm(instance=attendance)

    return render(request, 'attendance/attendance_form.html', {
        'form': form,
        'title': 'Modifier une présence'
    })