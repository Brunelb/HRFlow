from django.urls import path
from .views import employee_list, employee_detail, employee_create, employee_update

urlpatterns = [
    path('', employee_list, name='employee_list'),
    path('create/', employee_create, name='employee_create'),
    path('<int:pk>/', employee_detail, name='employee_detail'),
    path('<int:pk>/edit/', employee_update, name='employee_update'),
]