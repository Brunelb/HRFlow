from django import forms
from .models import Employee

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