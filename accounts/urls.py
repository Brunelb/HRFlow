from django.urls import path
from .views import (
    role_redirect_view,
    user_list,
    user_create,
    user_update,
)

urlpatterns = [
    path('redirect/', role_redirect_view, name='role_redirect'),

    path('users/', user_list, name='user_list'),
    path('users/create/', user_create, name='user_create'),
    path('users/<int:pk>/edit/', user_update, name='user_update'),
]