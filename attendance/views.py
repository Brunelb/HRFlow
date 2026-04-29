from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.db.models import Q
from django.core.paginator import Paginator

from .models import Attendance
from .forms import AttendanceCheckInOutForm, AttendanceAdminForm
from employees.models import Employee
from accounts.decorators import role_required


@login_required
def attendance_list(request):
    user = request.user

    search_query = request.GET.get('q', '').strip()
    date = request.GET.get('date', '').strip()
    status = request.GET.get('status', '').strip()
    per_page = request.GET.get('per_page', '10')

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

    attendances = attendances.select_related(
        'employee',
        'employee__user',
        'employee__department',
        'employee__manager',
    ).order_by('-date', '-check_in')

    if search_query:
        attendances = attendances.filter(
            Q(employee__user__first_name__icontains=search_query) |
            Q(employee__user__last_name__icontains=search_query) |
            Q(employee__user__username__icontains=search_query) |
            Q(employee__user__email__icontains=search_query) |
            Q(employee__employee_id__icontains=search_query)
        )

    if date:
        attendances = attendances.filter(date=date)

    if status:
        attendances = attendances.filter(status=status)

    if per_page not in ['10', '20']:
        per_page = '10'

    paginator = Paginator(attendances, int(per_page))
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'attendance/attendance_list.html', {
        'attendances': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
        'selected_date': date,
        'selected_status': status,
        'per_page': per_page,
        'status_choices': Attendance.STATUS_CHOICES,
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

            try:
                attendance.save()
                messages.success(request, "Votre présence a été enregistrée.")
                return redirect('attendance_list')
            except IntegrityError:
                form.add_error('date', "Une présence existe déjà pour cette date.")
    else:
        form = AttendanceCheckInOutForm()

    return render(request, 'attendance/attendance_form.html', {
        'form': form,
        'title': 'Enregistrer ma présence'
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
            try:
                form.save()
                messages.success(request, "La présence a été ajoutée avec succès.")
                return redirect('attendance_list')
            except IntegrityError:
                form.add_error('date', "Une présence existe déjà pour cet employé à cette date.")
    else:
        form = AttendanceAdminForm()

    return render(request, 'attendance/attendance_form.html', {
        'form': form,
        'title': 'Ajouter une présence'
    })


@login_required
@role_required(['hr', 'admin'])
def attendance_update(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)

    if request.method == 'POST':
        form = AttendanceAdminForm(request.POST, instance=attendance)

        if form.is_valid():
            form.save()
            messages.success(request, "La présence a été modifiée avec succès.")
            return redirect('attendance_detail', pk=attendance.pk)
    else:
        form = AttendanceAdminForm(instance=attendance)

    return render(request, 'attendance/attendance_form.html', {
        'form': form,
        'title': 'Modifier une présence'
    })