from django.urls import path
from .views import (
    attendance_list,
    attendance_create,
    attendance_detail,
    attendance_admin_create,
    attendance_update,
)

urlpatterns = [
    path('', attendance_list, name='attendance_list'),
    path('create/', attendance_create, name='attendance_create'),
    path('admin-create/', attendance_admin_create, name='attendance_admin_create'),
    path('<int:pk>/', attendance_detail, name='attendance_detail'),
    path('<int:pk>/edit/', attendance_update, name='attendance_update'),
]