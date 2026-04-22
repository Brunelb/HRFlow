from django.db import models
from employees.models import Employee
from django.conf import settings
from django.core.exceptions import ValidationError

class LeaveRequest(models.Model):
    LEAVE_TYPE_CHOICES = (
        ('annual', 'Congé annuel'),
        ('sick', 'Congé maladie'),
        ('special', 'Congé exceptionnel'),
        ('maternity', 'Congé maternité'),
    )

    STATUS_CHOICES = (
        ('pending_manager', 'En attente du manager'),
        ('pending_hr', 'En attente RH'),
        ('approved', 'Approuvé'),
        ('rejected', 'Refusé'),
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='leave_requests'
    )
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES, default='annual')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending_manager')

    manager_comment = models.TextField(blank=True)
    hr_comment = models.TextField(blank=True)

    approved_by_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_leave_approvals'
    )
    approved_by_hr = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hr_leave_approvals'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError("La date de fin ne peut pas être antérieure à la date de début.")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee} - {self.get_leave_type_display()} ({self.get_status_display()})"