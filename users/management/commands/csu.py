from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        email = "admin@gmail.com"
        username = "admin"

        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f"User with email {email} already exists")
            )
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f"User with username {username} already exists")
            )
            return

        user = User.objects.create(
            username=username,
            email=email,
            is_staff=True,
            is_superuser=True,
            is_active=True,
        )
        user.set_password("admin")
        user.save()
        self.stdout.write(
            self.style.SUCCESS(f"Superuser {user.email} created successfully")
        )
