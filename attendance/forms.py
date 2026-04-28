from django import forms
from django.utils import timezone
from datetime import timedelta

from .models import Attendance


class AttendanceCheckInOutForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = [
            'date',
            'check_in',
            'check_out',
            'note',
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'check_in': forms.TimeInput(attrs={'type': 'time'}),
            'check_out': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean_date(self):
        selected_date = self.cleaned_data.get('date')
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)

        if selected_date > today:
            raise forms.ValidationError("Vous ne pouvez pas pointer une date future.")

        if selected_date < yesterday:
            raise forms.ValidationError("Vous pouvez seulement pointer aujourd’hui ou hier.")

        return selected_date


class AttendanceAdminForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = [
            'employee',
            'date',
            'check_in',
            'check_out',
            'status',
            'note',
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'check_in': forms.TimeInput(attrs={'type': 'time'}),
            'check_out': forms.TimeInput(attrs={'type': 'time'}),
        }