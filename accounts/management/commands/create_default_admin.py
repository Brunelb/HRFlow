import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create or update default admin user for production deployment"

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.environ.get("ADMIN_USERNAME", "admin")
        email = os.environ.get("ADMIN_EMAIL", "admin@example.com")
        password = os.environ.get("ADMIN_PASSWORD")
        reset_password = os.environ.get("RESET_ADMIN_PASSWORD", "False") == "True"

        if not password:
            self.stdout.write(self.style.ERROR("ADMIN_PASSWORD is not defined"))
            return

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_staff": True,
                "is_superuser": True,
                "role": "admin",
            }
        )

        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.role = "admin"

        if created or reset_password:
            user.set_password(password)

        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f"Admin user '{username}' created successfully"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Admin user '{username}' updated successfully"))