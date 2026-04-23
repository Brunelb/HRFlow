from django.urls import path
from .views import (
    document_list,
    document_detail,
    document_create,
    document_update,
    document_delete,
)

urlpatterns = [
    path('', document_list, name='document_list'),
    path('create/', document_create, name='document_create'),
    path('<int:pk>/', document_detail, name='document_detail'),
    path('<int:pk>/edit/', document_update, name='document_update'),
    path('<int:pk>/delete/', document_delete, name='document_delete'),
]