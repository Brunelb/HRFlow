from django import forms
from .models import LeaveRequest

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class ManagerLeaveApprovalForm(forms.ModelForm):
    manager_decision = forms.ChoiceField(
        choices=(
            ('approve', 'Approuver'),
            ('reject', 'Refuser'),
        ),
        label='Décision du manager'
    )

    class Meta:
        model = LeaveRequest
        fields = ['manager_comment']

class HRLeaveApprovalForm(forms.ModelForm):
    hr_decision = forms.ChoiceField(
        choices=(
            ('approve', 'Approuver'),
            ('reject', 'Refuser'),
        ),
        label='Décision RH'
    )

    class Meta:
        model = LeaveRequest
        fields = ['hr_comment']