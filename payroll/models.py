from django.db import models
from employees.models import Employee
from django.conf import settings
from django.utils import timezone


class Payroll(models.Model):

    MONTH_CHOICES = [
        (1, 'Janvier'),
        (2, 'Février'),
        (3, 'Mars'),
        (4, 'Avril'),
        (5, 'Mai'),
        (6, 'Juin'),
        (7, 'Juillet'),
        (8, 'Août'),
        (9, 'Septembre'),
        (10, 'Octobre'),
        (11, 'Novembre'),
        (12, 'Décembre'),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='payrolls'
    )

    month = models.PositiveSmallIntegerField(
        choices=MONTH_CHOICES,
        default=1
    )

    year = models.PositiveIntegerField(
        default=timezone.now().year
    )

    base_salary = models.DecimalField(max_digits=10, decimal_places=2)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    net_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False
    )

    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generated_payrolls'
    )

    note = models.TextField(blank=True)

    generated_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year', '-month', '-generated_at']
        unique_together = ('employee', 'month', 'year')

    def save(self, *args, **kwargs):
        self.net_salary = (self.base_salary + self.bonus) - self.deductions
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee} - {self.get_month_display()}/{self.year}"


class SalaryHistory(models.Model):

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='salary_history'
    )

    old_salary = models.DecimalField(max_digits=10, decimal_places=2)
    new_salary = models.DecimalField(max_digits=10, decimal_places=2)

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='salary_changes'
    )

    reason = models.TextField(blank=True)

    changed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.employee} - {self.old_salary} → {self.new_salary}"