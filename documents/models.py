from django.db import models
from employees.models import Employee

class Document(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)