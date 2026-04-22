from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class AdminUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
            'is_active',
        )

class AdminUserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
            'is_active',
        )