from django.db import models
from django.conf import settings
from departments.models import Department

class Employee(models.Model):
    STATUS_CHOICES = (
        ('active', 'Actif'),
        ('suspended', 'Suspendu'),
        ('leave', 'En congé'),
        ('inactive', 'Inactif'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employee_profile'
    )
    employee_id = models.CharField(max_length=20, unique=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    hire_date = models.DateField()
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees'
    )
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='team_members'
    )
    base_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    profile_photo = models.ImageField(upload_to='employees/photos/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['employee_id']

    def save(self, *args, **kwargs):
        if not self.employee_id:
            last_employee = Employee.objects.order_by('id').last()
            next_id = 1 if not last_employee else last_employee.id + 1
            self.employee_id = f"EMP{next_id:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name() or self.user.username}"