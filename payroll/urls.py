from django.urls import path

from .views import (
    payroll_list,
    payroll_detail,
    payroll_create,
    payroll_update,
    payroll_delete,
    payroll_payslip,
    salary_history_list,
    salary_history_create,
)

urlpatterns = [
    path('', payroll_list, name='payroll_list'),
    path('create/', payroll_create, name='payroll_create'),

    path('salary-history/', salary_history_list, name='salary_history_list'),
    path('salary-history/create/', salary_history_create, name='salary_history_create'),

    path('<int:pk>/', payroll_detail, name='payroll_detail'),
    path('<int:pk>/edit/', payroll_update, name='payroll_update'),
    path('<int:pk>/delete/', payroll_delete, name='payroll_delete'),

    path('<int:pk>/payslip/', payroll_payslip, name='payroll_payslip'),
]