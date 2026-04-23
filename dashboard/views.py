from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Sum

from accounts.decorators import role_required
from employees.models import Employee
from departments.models import Department
from leaves.models import LeaveRequest
from attendance.models import Attendance
from documents.models import Document
from payroll.models import Payroll

@login_required
@role_required(['admin'])
def admin_dashboard(request):
    today = timezone.now().date()

    total_employees = Employee.objects.count()
    total_departments = Department.objects.count()
    pending_leaves = LeaveRequest.objects.filter(status__in=['pending_manager', 'pending_hr']).count()
    today_absences = Attendance.objects.filter(date=today, status='absent').count()
    payroll_total = Payroll.objects.aggregate(total=Sum('net_salary'))['total'] or 0
    recent_documents = Document.objects.select_related('employee').all()[:5]

    context = {
        'total_employees': total_employees,
        'total_departments': total_departments,
        'pending_leaves': pending_leaves,
        'today_absences': today_absences,
        'payroll_total': payroll_total,
        'recent_documents': recent_documents,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
@role_required(['hr'])
def hr_dashboard(request):
    today = timezone.now().date()

    total_employees = Employee.objects.count()
    pending_hr_leaves = LeaveRequest.objects.filter(status='pending_hr').count()
    today_absences = Attendance.objects.filter(date=today, status='absent').count()
    recent_documents = Document.objects.select_related('employee').all()[:5]

    context = {
        'total_employees': total_employees,
        'pending_hr_leaves': pending_hr_leaves,
        'today_absences': today_absences,
        'recent_documents': recent_documents,
    }
    return render(request, 'dashboard/hr_dashboard.html', context)


@login_required
@role_required(['manager'])
def manager_dashboard(request):
    team_members = Employee.objects.filter(manager=request.user)
    team_count = team_members.count()
    pending_team_leaves = LeaveRequest.objects.filter(
        employee__manager=request.user,
        status='pending_manager'
    ).count()
    team_today_absences = Attendance.objects.filter(
        employee__manager=request.user,
        date=timezone.now().date(),
        status='absent'
    ).count()

    context = {
        'team_count': team_count,
        'pending_team_leaves': pending_team_leaves,
        'team_today_absences': team_today_absences,
    }
    return render(request, 'dashboard/manager_dashboard.html', context)

@login_required
@role_required(['employee'])
def employee_dashboard(request):
    employee = getattr(request.user, 'employee_profile', None)

    my_leaves = LeaveRequest.objects.filter(employee=employee).count() if employee else 0
    my_pending_leaves = LeaveRequest.objects.filter(
        employee=employee,
        status__in=['pending_manager', 'pending_hr']
    ).count() if employee else 0
    my_documents = Document.objects.filter(employee=employee).count() if employee else 0
    my_payrolls = Payroll.objects.filter(employee=employee).count() if employee else 0

    context = {
        'my_leaves': my_leaves,
        'my_pending_leaves': my_pending_leaves,
        'my_documents': my_documents,
        'my_payrolls': my_payrolls,
    }
    return render(request, 'dashboard/employee_dashboard.html', context)