from django.urls import path
from .views import department_list, department_create, department_update

urlpatterns = [
    path('', department_list, name='department_list'),
    path('create/', department_create, name='department_create'),
    path('<int:pk>/edit/', department_update, name='department_update'),
]