from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import User
from .forms import AdminUserCreationForm, AdminUserUpdateForm
from .decorators import role_required

@login_required
def role_redirect_view(request):
    user = request.user

    if user.is_superuser or user.role == 'admin':
        return redirect('admin_dashboard')
    elif user.role == 'hr':
        return redirect('hr_dashboard')
    elif user.role == 'manager':
        return redirect('manager_dashboard')
    else:
        return redirect('employee_dashboard')


@login_required
@role_required(['admin'])
def user_list(request):
    users = User.objects.all().order_by('username')

    users_with_employee_flag = []
    for user in users:
        users_with_employee_flag.append({
            'obj': user,
            'has_employee_profile': hasattr(user, 'employee_profile')
        })

    return render(request, 'accounts/user_list.html', {
        'users_with_employee_flag': users_with_employee_flag
    })


@login_required
@role_required(['admin'])
def user_create(request):
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = AdminUserCreationForm()

    return render(request, 'accounts/user_form.html', {
        'form': form,
        'title': 'Créer un utilisateur'
    })


@login_required
@role_required(['admin'])
def user_update(request, pk):
    user_obj = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        form = AdminUserUpdateForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = AdminUserUpdateForm(instance=user_obj)

    return render(request, 'accounts/user_form.html', {
        'form': form,
        'title': 'Modifier un utilisateur'
    })