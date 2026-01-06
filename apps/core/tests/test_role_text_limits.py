from django.test import TestCase

from apps.core.models import RoleTextLimit


class RoleTextLimitMigrationTest(TestCase):
    def test_role_text_limits_exist_after_migrations(self):
        """Ensure seeded RoleTextLimit rows exist after migrations."""
        expected = [
            "Anonymous",
            "RegisteredFree",
            "SubscriberPaid",
            "Moderator",
            "Staff",
            "Admin",
        ]

        existing = list(
            RoleTextLimit.objects.filter(role_name__in=expected).values_list(
                "role_name", flat=True
            )
        )
        missing = [r for r in expected if r not in existing]
        self.assertFalse(missing, msg=f"Missing seeded RoleTextLimit rows: {missing}")
