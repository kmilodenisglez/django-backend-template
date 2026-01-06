from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class RBACTests(TestCase):
    def setUp(self):
        pass

    def test_user_permissions(self):
        # Regular user shouldn't have these by default via group (unless added elsewhere)
        self.assertFalse(self.regular_user.has_perm("classifieds.change_category"))
