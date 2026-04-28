from django import forms

from .models import Employee
from accounts.models import User


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'user',
            'phone',
            'address',
            'hire_date',
            'department',
            'manager',
            'base_salary',
            'profile_photo',
            'status',
        ]
        widgets = {
            'hire_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        linked_user_ids = Employee.objects.exclude(
            pk=self.instance.pk if self.instance and self.instance.pk else None
        ).values_list('user_id', flat=True)

        self.fields['user'].queryset = User.objects.filter(
            role__in=['hr', 'manager', 'employee']
        ).exclude(
            id__in=linked_user_ids
        ).order_by('username')

        self.fields['manager'].queryset = User.objects.filter(
            role='manager'
        ).order_by('username')

        self.fields['manager'].required = False