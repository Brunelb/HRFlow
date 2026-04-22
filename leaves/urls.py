from django.urls import path
from .views import (
    leave_list,
    leave_create,
    leave_detail,
    manager_leave_approval,
    hr_leave_approval,
)

urlpatterns = [
    path('', leave_list, name='leave_list'),
    path('create/', leave_create, name='leave_create'),
    path('<int:pk>/', leave_detail, name='leave_detail'),
    path('<int:pk>/manager-approval/', manager_leave_approval, name='manager_leave_approval'),
    path('<int:pk>/hr-approval/', hr_leave_approval, name='hr_leave_approval'),
]