from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied

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

            # Ancien salaire récupéré automatiquement depuis la fiche employé
            history.old_salary = history.employee.base_salary

            history.save()

            # Mise à jour du salaire actuel de l’employé
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