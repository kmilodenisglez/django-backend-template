from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from .models import Discount, Plan, Subscription

User = get_user_model()


class SubscriptionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.plan = Plan.objects.create(
            name="Monthly",
            slug="monthly",
            price=10.00,
            duration_months=1,
            stripe_price_id="price_123",
        )
        self.discount = Discount.objects.create(
            name="Long Term", duration_months=12, percentage_off=20
        )

    def test_plan_creation(self):
        self.assertEqual(self.plan.name, "Monthly")
        self.assertEqual(self.plan.get_duration_display(), "Monthly")

    def test_subscription_creation(self):
        sub = Subscription.objects.create(
            user=self.user,
            plan=self.plan,
            status=Subscription.STATUS_ACTIVE,
            end_date=timezone.now() + timezone.timedelta(days=30),
        )
        self.assertTrue(sub.is_active)
        self.assertEqual(sub.user, self.user)

    def test_discount_logic(self):
        # This is a basic test for model existence, actual discount application logic
        # would be in the view or a service method which we haven't fully implemented
        # beyond the model structure.
        self.assertEqual(self.discount.percentage_off, 20)
