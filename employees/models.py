from django.db import models
from accounts.models import User
from departments.models import Department

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=10, unique=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    hire_date = models.DateField()
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='team')
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.user.username