from django import forms
from .models import Payroll, SalaryHistory


class PayrollForm(forms.ModelForm):
    class Meta:
        model = Payroll
        fields = [
            'employee',
            'month',
            'year',
            'base_salary',
            'bonus',
            'deductions',
            'note',
        ]


class SalaryHistoryForm(forms.ModelForm):
    class Meta:
        model = SalaryHistory
        fields = [
            'employee',
            'old_salary',
            'new_salary',
            'reason',
        ]