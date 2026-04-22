from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied

from .models import LeaveRequest
from .forms import LeaveRequestForm, ManagerLeaveApprovalForm, HRLeaveApprovalForm
from employees.models import Employee
from accounts.decorators import role_required

@login_required
def leave_list(request):
    user = request.user

    if user.role == 'employee':
        try:
            employee = user.employee_profile
            leaves = LeaveRequest.objects.filter(employee=employee)
        except Employee.DoesNotExist:
            leaves = LeaveRequest.objects.none()

    elif user.role == 'manager':
        leaves = LeaveRequest.objects.filter(employee__manager=user)

    elif user.role in ['hr', 'admin']:
        leaves = LeaveRequest.objects.all()

    else:
        leaves = LeaveRequest.objects.none()

    return render(request, 'leaves/leave_list.html', {'leaves': leaves})

@login_required
@role_required(['employee', 'manager', 'hr'])
def leave_create(request):
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        raise PermissionDenied("Aucune fiche employé liée à ce compte.")

    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.employee = employee
            leave.status = 'pending_manager'
            leave.save()
            return redirect('leave_list')
    else:
        form = LeaveRequestForm()

    return render(request, 'leaves/leave_form.html', {
        'form': form,
        'title': 'Nouvelle demande de congé'
    })

@login_required
def leave_detail(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    user = request.user

    if user.role == 'employee':
        if not hasattr(user, 'employee_profile') or leave.employee != user.employee_profile:
            raise PermissionDenied

    elif user.role == 'manager':
        if leave.employee.manager != user:
            raise PermissionDenied

    elif user.role not in ['hr', 'admin']:
        raise PermissionDenied

    return render(request, 'leaves/leave_detail.html', {'leave': leave})

@login_required
@role_required(['manager'])
def manager_leave_approval(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)

    if leave.employee.manager != request.user:
        raise PermissionDenied

    if leave.status != 'pending_manager':
        raise PermissionDenied("Cette demande n'est pas en attente du manager.")

    if request.method == 'POST':
        form = ManagerLeaveApprovalForm(request.POST, instance=leave)
        if form.is_valid():
            decision = form.cleaned_data['manager_decision']
            leave = form.save(commit=False)
            leave.approved_by_manager = request.user

            if decision == 'approve':
                leave.status = 'pending_hr'
            else:
                leave.status = 'rejected'

            leave.save()
            return redirect('leave_list')
    else:
        form = ManagerLeaveApprovalForm(instance=leave)

    return render(request, 'leaves/leave_approval_form.html', {
        'form': form,
        'leave': leave,
        'title': 'Validation manager'
    })

@login_required
@role_required(['hr', 'admin'])
def hr_leave_approval(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)

    if leave.status != 'pending_hr':
        raise PermissionDenied("Cette demande n'est pas en attente RH.")

    if request.method == 'POST':
        form = HRLeaveApprovalForm(request.POST, instance=leave)
        if form.is_valid():
            decision = form.cleaned_data['hr_decision']
            leave = form.save(commit=False)
            leave.approved_by_hr = request.user

            if decision == 'approve':
                leave.status = 'approved'
            else:
                leave.status = 'rejected'

            leave.save()
            return redirect('leave_list')
    else:
        form = HRLeaveApprovalForm(instance=leave)

    return render(request, 'leaves/leave_approval_form.html', {
        'form': form,
        'leave': leave,
        'title': 'Validation RH'
    })