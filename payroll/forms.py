from django import forms
from .models import Payroll, SalaryHistory


class PayrollForm(forms.ModelForm):
    class Meta:
        model = Payroll
        fields = [
            'employee',
            'month',
            'year',
            'bonus',
            'deductions',
            'note',
        ]


class SalaryHistoryForm(forms.ModelForm):
    class Meta:
        model = SalaryHistory
        fields = [
            'employee',
            'new_salary',
            'reason',
        ]

    def __init__(self, *args, **kwargs):
        selected_employee = kwargs.pop('selected_employee', None)
        super().__init__(*args, **kwargs)

        if selected_employee:
            self.fields['employee'].initial = selected_employee
            self.fields['employee'].widget.attrs['readonly'] = True