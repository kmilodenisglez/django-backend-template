from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.core.models import RoleImageLimit, RoleTextLimit

User = get_user_model()


class LimitsAPITest(TestCase):
    def setUp(self):
        # ensure seeded rows exist
        self.anonymous_text = RoleTextLimit.objects.get(role_name__iexact="Anonymous")
        self.registered_text = RoleTextLimit.objects.get(
            role_name__iexact="RegisteredFree"
        )
        self.admin_text = RoleTextLimit.objects.get(role_name__iexact="Admin")

        self.anonymous_image = RoleImageLimit.objects.filter(
            role_name__iexact="RegisteredFree"
        ).first()
        # image limits may be stored under RegisteredFree for registered users;
        # for anonymous we expect RegisteredFree or default behavior in utils

        self.client = APIClient()

    def test_limits_anonymous(self):
        resp = self.client.get("/api/core/limits/")
        assert resp.status_code == 200, resp.content
        data = resp.json()
        assert "image_max" in data
        assert "text_limits" in data
        self.assertEqual(data["text_limits"]["title"], self.anonymous_text.title_limit)
        self.assertEqual(data["text_limits"]["body"], self.anonymous_text.body_limit)

    def test_limits_registered_free(self):
        user = User.objects.create_user(
            username="freeuser2", email="free2@example.com", password="pass"
        )
        self.client.force_authenticate(user=user)
        resp = self.client.get("/api/core/limits/")
        assert resp.status_code == 200, resp.content
        data = resp.json()
        self.assertEqual(data["text_limits"]["title"], self.registered_text.title_limit)
        self.assertEqual(data["text_limits"]["body"], self.registered_text.body_limit)
        # image_max should be present and an int
        self.assertIsInstance(data.get("image_max"), int)

    def test_limits_admin(self):
        admin = User.objects.create_user(
            username="admin2",
            email="admin2@example.com",
            password="pass",
            is_superuser=True,
            is_staff=True,
        )
        self.client.force_authenticate(user=admin)
        resp = self.client.get("/api/core/limits/")
        assert resp.status_code == 200, resp.content
        data = resp.json()
        self.assertEqual(data["text_limits"]["title"], self.admin_text.title_limit)
        self.assertEqual(data["text_limits"]["body"], self.admin_text.body_limit)
