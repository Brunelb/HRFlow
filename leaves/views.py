from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied

from .models import LeaveRequest
from .forms import LeaveRequestForm, ManagerLeaveApprovalForm, HRLeaveApprovalForm
from employees.models import Employee
from accounts.decorators import role_required
from django.core.paginator import Paginator
from django.db.models import Q

@login_required
def leave_list(request):
    user = request.user

    search_query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    per_page = request.GET.get('per_page', '10')

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

    leaves = leaves.select_related('employee', 'employee__user').order_by('-created_at')

    if search_query:
        leaves = leaves.filter(
            Q(employee__user__first_name__icontains=search_query) |
            Q(employee__user__last_name__icontains=search_query) |
            Q(employee__user__username__icontains=search_query) |
            Q(employee__employee_id__icontains=search_query)
        )

    if status:
        leaves = leaves.filter(status=status)

    if per_page not in ['10', '20']:
        per_page = '10'

    paginator = Paginator(leaves, int(per_page))
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'leaves/leave_list.html', {
        'leaves': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
        'selected_status': status,
        'per_page': per_page,
        'status_choices': LeaveRequest.STATUS_CHOICES,
    })

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