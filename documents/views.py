from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied

from .models import Document
from .forms import DocumentForm
from accounts.decorators import role_required
from employees.models import Employee

@login_required
def document_list(request):
    user = request.user

    if user.role == 'employee':
        try:
            employee = user.employee_profile
            documents = Document.objects.filter(employee=employee)
        except Employee.DoesNotExist:
            documents = Document.objects.none()

    elif user.role == 'manager':
        documents = Document.objects.filter(employee__manager=user)

    elif user.role in ['hr', 'admin']:
        documents = Document.objects.all()

    else:
        documents = Document.objects.none()

    return render(request, 'documents/document_list.html', {
        'documents': documents
    })

@login_required
def document_detail(request, pk):
    document = get_object_or_404(Document, pk=pk)
    user = request.user

    if user.role == 'employee':
        if not hasattr(user, 'employee_profile') or document.employee != user.employee_profile:
            raise PermissionDenied

    elif user.role == 'manager':
        if document.employee.manager != user:
            raise PermissionDenied

    elif user.role not in ['hr', 'admin']:
        raise PermissionDenied

    return render(request, 'documents/document_detail.html', {
        'document': document
    })

@login_required
@role_required(['hr', 'admin'])
def document_create(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.uploaded_by = request.user
            document.save()
            return redirect('document_list')
    else:
        form = DocumentForm()

    return render(request, 'documents/document_form.html', {
        'form': form,
        'title': 'Ajouter un document'
    })

@login_required
@role_required(['hr', 'admin'])
def document_update(request, pk):
    document = get_object_or_404(Document, pk=pk)

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            updated_document = form.save(commit=False)
            if not updated_document.uploaded_by:
                updated_document.uploaded_by = request.user
            updated_document.save()
            return redirect('document_detail', pk=document.pk)
    else:
        form = DocumentForm(instance=document)

    return render(request, 'documents/document_form.html', {
        'form': form,
        'title': 'Modifier un document'
    })

@login_required
@role_required(['hr', 'admin'])
def document_delete(request, pk):
    document = get_object_or_404(Document, pk=pk)

    if request.method == 'POST':
        document.delete()
        return redirect('document_list')

    return render(request, 'documents/document_confirm_delete.html', {
        'document': document
    })