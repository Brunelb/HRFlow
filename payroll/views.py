from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Payroll, SalaryHistory
from .forms import PayrollForm, SalaryHistoryForm
from employees.models import Employee
from accounts.decorators import role_required


def can_access_payroll(user, payroll):
    if user.role in ['admin', 'hr']:
        return True

    if user.role == 'employee':
        return hasattr(user, 'employee_profile') and payroll.employee == user.employee_profile

    return False


@login_required
def payroll_list(request):
    user = request.user

    search_query = request.GET.get('q', '').strip()
    month = request.GET.get('month', '').strip()
    year = request.GET.get('year', '').strip()
    per_page = request.GET.get('per_page', '10')

    if user.role == 'employee':
        try:
            employee = user.employee_profile
            payrolls = Payroll.objects.filter(employee=employee)
        except Employee.DoesNotExist:
            payrolls = Payroll.objects.none()

    elif user.role in ['hr', 'admin']:
        payrolls = Payroll.objects.all()

    else:
        payrolls = Payroll.objects.none()

    payrolls = payrolls.select_related(
        'employee',
        'employee__user',
        'employee__department',
        'generated_by'
    )

    if search_query:
        payrolls = payrolls.filter(
            Q(employee__user__first_name__icontains=search_query) |
            Q(employee__user__last_name__icontains=search_query) |
            Q(employee__user__username__icontains=search_query) |
            Q(employee__employee_id__icontains=search_query)
        )

    if month:
        payrolls = payrolls.filter(month=month)

    if year:
        payrolls = payrolls.filter(year=year)

    if per_page not in ['10', '20']:
        per_page = '10'

    paginator = Paginator(payrolls, int(per_page))
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    years = Payroll.objects.values_list('year', flat=True).distinct().order_by('-year')

    return render(request, 'payroll/payroll_list.html', {
        'payrolls': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
        'selected_month': month,
        'selected_year': year,
        'per_page': per_page,
        'month_choices': Payroll.MONTH_CHOICES,
        'years': years,
    })


@login_required
def payroll_detail(request, pk):
    payroll = get_object_or_404(Payroll, pk=pk)

    if not can_access_payroll(request.user, payroll):
        raise PermissionDenied

    return render(request, 'payroll/payroll_detail.html', {
        'payroll': payroll
    })


@login_required
def payroll_payslip(request, pk):
    payroll = get_object_or_404(Payroll, pk=pk)

    if not can_access_payroll(request.user, payroll):
        raise PermissionDenied

    return render(request, 'payroll/payroll_payslip.html', {
        'payroll': payroll
    })


@login_required
@role_required(['hr', 'admin'])
def payroll_create(request):
    if request.method == 'POST':
        form = PayrollForm(request.POST)

        if form.is_valid():
            payroll = form.save(commit=False)
            payroll.generated_by = request.user
            payroll.base_salary = payroll.employee.base_salary
            payroll.save()

            messages.success(request, "La fiche de paie a été créée avec succès.")
            return redirect('payroll_detail', pk=payroll.pk)
    else:
        form = PayrollForm()

    return render(request, 'payroll/payroll_form.html', {
        'form': form,
        'title': 'Créer une fiche de paie'
    })


@login_required
@role_required(['hr', 'admin'])
def payroll_update(request, pk):
    payroll = get_object_or_404(Payroll, pk=pk)

    if request.method == 'POST':
        form = PayrollForm(request.POST, instance=payroll)

        if form.is_valid():
            updated_payroll = form.save(commit=False)
            updated_payroll.base_salary = updated_payroll.employee.base_salary
            updated_payroll.save()

            messages.success(request, "La fiche de paie a été modifiée avec succès.")
            return redirect('payroll_detail', pk=payroll.pk)
    else:
        form = PayrollForm(instance=payroll)

    return render(request, 'payroll/payroll_form.html', {
        'form': form,
        'title': 'Modifier une fiche de paie'
    })


@login_required
@role_required(['hr', 'admin'])
def payroll_delete(request, pk):
    payroll = get_object_or_404(Payroll, pk=pk)

    if request.method == 'POST':
        payroll.delete()
        messages.success(request, "La fiche de paie a été supprimée avec succès.")
        return redirect('payroll_list')

    return render(request, 'payroll/payroll_confirm_delete.html', {
        'payroll': payroll
    })


@login_required
@role_required(['hr', 'admin'])
def salary_history_list(request):
    history = SalaryHistory.objects.select_related('employee', 'changed_by').all()

    return render(request, 'payroll/salary_history_list.html', {
        'history': history
    })


@login_required
@role_required(['hr', 'admin'])
def salary_history_create(request):
    employee_id = request.GET.get('employee') or request.POST.get('employee')
    selected_employee = None

    if employee_id:
        selected_employee = get_object_or_404(Employee, pk=employee_id)

    if request.method == 'POST':
        form = SalaryHistoryForm(
            request.POST,
            selected_employee=selected_employee
        )

        if form.is_valid():
            history = form.save(commit=False)
            history.changed_by = request.user
            history.old_salary = history.employee.base_salary
            history.save()

            employee = history.employee
            employee.base_salary = history.new_salary
            employee.save()

            messages.success(request, "Le changement de salaire a été enregistré.")
            return redirect('salary_history_list')
    else:
        form = SalaryHistoryForm(selected_employee=selected_employee)

    return render(request, 'payroll/salary_history_form.html', {
        'form': form,
        'title': 'Enregistrer un changement de salaire',
        'selected_employee': selected_employee,
    })