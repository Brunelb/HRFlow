from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied

from .models import Payroll, SalaryHistory
from .forms import PayrollForm, SalaryHistoryForm
from employees.models import Employee
from accounts.decorators import role_required

@login_required
def payroll_list(request):
    user = request.user

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

    return render(request, 'payroll/payroll_list.html', {
        'payrolls': payrolls
    })

@login_required
def payroll_detail(request, pk):
    payroll = get_object_or_404(Payroll, pk=pk)
    user = request.user

    if user.role == 'employee':
        if not hasattr(user, 'employee_profile') or payroll.employee != user.employee_profile:
            raise PermissionDenied

    elif user.role not in ['hr', 'admin']:
        raise PermissionDenied

    return render(request, 'payroll/payroll_detail.html', {
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
            payroll.save()
            return redirect('payroll_list')
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
            form.save()
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
        return redirect('payroll_list')

    return render(request, 'payroll/payroll_confirm_delete.html', {
        'payroll': payroll
    })

@login_required
@role_required(['hr', 'admin'])
def salary_history_list(request):
    history = SalaryHistory.objects.all()
    return render(request, 'payroll/salary_history_list.html', {
        'history': history
    })


@login_required
@role_required(['hr', 'admin'])
def salary_history_create(request):
    if request.method == 'POST':
        form = SalaryHistoryForm(request.POST)
        if form.is_valid():
            history = form.save(commit=False)
            history.changed_by = request.user
            history.save()

            # mise à jour du salaire dans Employee
            employee = history.employee
            employee.base_salary = history.new_salary
            employee.save()

            return redirect('salary_history_list')
    else:
        form = SalaryHistoryForm()

    return render(request, 'payroll/salary_history_form.html', {
        'form': form,
        'title': 'Changement de salaire'
    })