from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.core.models import RoleTextLimit
from apps.core.utils import get_user_text_limits

User = get_user_model()


class UserTextLimitsTest(TestCase):
    def setUp(self):
        # Ensure seed data exists (migration should have run)
        self.anonymous_limits = RoleTextLimit.objects.get(role_name__iexact="Anonymous")
        self.registered_limits = RoleTextLimit.objects.get(
            role_name__iexact="RegisteredFree"
        )
        self.admin_limits = RoleTextLimit.objects.get(role_name__iexact="Admin")

    def test_anonymous_user_text_limits(self):
        limits = get_user_text_limits(None)
        self.assertEqual(limits["title"], self.anonymous_limits.title_limit)
        self.assertEqual(limits["body"], self.anonymous_limits.body_limit)

    def test_registered_free_user_text_limits(self):
        user = User.objects.create_user(
            username="freeuser", email="free@example.com", password="password"
        )
        limits = get_user_text_limits(user)
        self.assertEqual(limits["title"], self.registered_limits.title_limit)
        self.assertEqual(limits["body"], self.registered_limits.body_limit)

    def test_admin_user_text_limits(self):
        admin = User.objects.create_user(
            username="adminuser",
            email="admin@example.com",
            password="password",
            is_superuser=True,
            is_staff=True,
        )
        limits = get_user_text_limits(admin)
        self.assertEqual(limits["title"], self.admin_limits.title_limit)
        self.assertEqual(limits["body"], self.admin_limits.body_limit)
