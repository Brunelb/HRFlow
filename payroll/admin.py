from django.contrib import admin
from .models import Payroll, SalaryHistory

admin.site.register(Payroll)
admin.site.register(SalaryHistory)