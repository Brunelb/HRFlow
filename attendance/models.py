from django.db import models
from employees.models import Employee
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

class Attendance(models.Model):
    STATUS_CHOICES = (
        ('present', 'Présent'),
        ('late', 'Retard'),
        ('absent', 'Absent'),
        ('half_day', 'Demi-journée'),
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    date = models.DateField()
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present')
    worked_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        unique_together = ('employee', 'date')

    def clean(self):
        if self.check_in and self.check_out and self.check_out < self.check_in:
            raise ValidationError("L'heure de départ ne peut pas être antérieure à l'heure d'arrivée.")

    def save(self, *args, **kwargs):
        if self.check_in and self.check_out:
            start = datetime.combine(self.date, self.check_in)
            end = datetime.combine(self.date, self.check_out)
            duration = end - start
            self.worked_hours = round(duration.total_seconds() / 3600, 2)

        if self.check_in:
            reference_time = datetime.strptime("08:30", "%H:%M").time()
            if self.check_in > reference_time and self.status == 'present':
                self.status = 'late'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee} - {self.date} - {self.get_status_display()}"