from django.db import models
from employees.models import Employee
from django.conf import settings

class Document(models.Model):
    DOCUMENT_TYPE_CHOICES = (
        ('contract', 'Contrat'),
        ('cv', 'CV'),
        ('id_card', "Pièce d'identité"),
        ('medical', 'Certificat médical'),
        ('administrative', 'Document administratif'),
        ('other', 'Autre'),
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPE_CHOICES, default='contrat')
    title = models.CharField(max_length=150, default="Sans titre")
    file = models.FileField(upload_to='documents/')
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_documents'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.title} - {self.employee}"