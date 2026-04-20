from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Department
from .forms import DepartmentForm
from accounts.decorators import role_required

@login_required
@role_required(['admin', 'hr'])
def department_list(request):
    departments = Department.objects.select_related('manager').all()
    return render(request, 'departments/department_list.html', {'departments': departments})

@login_required
@role_required(['admin', 'hr'])
def department_create(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('department_list')
    else:
        form = DepartmentForm()
    return render(request, 'departments/department_form.html', {'form': form, 'title': 'Créer un département'})

@login_required
@role_required(['admin', 'hr'])
def department_update(request, pk):
    department = get_object_or_404(Department, pk=pk)

    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            return redirect('department_list')
    else:
        form = DepartmentForm(instance=department)

    return render(request, 'departments/department_form.html', {'form': form, 'title': 'Modifier le département'})