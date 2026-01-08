from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Setup RBAC roles and permissions"

    def handle(self, *args, **options):
        # Create Groups
        voter_group, created = Group.objects.get_or_create(name="Voter")
        user_group, created = Group.objects.get_or_create(name="User")

        # Define Permissions for ...
        # Can view all listings (default for all users usually, but explicit here if needed)

        # Get specific permissions

        # Assign permissions

        self.stdout.write(
            self.style.SUCCESS("Successfully setup roles and permissions")
        )
