from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import PaymentMethod, Plan
from .services import NowPaymentsProvider, PaymentFactory, StripeProvider

User = get_user_model()


class PaymentSystemTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.plan = Plan.objects.create(
            name="Monthly",
            slug="monthly",
            price=10.00,
            duration_months=1,
            stripe_price_id="price_123",
        )
        self.stripe_method = PaymentMethod.objects.create(
            name="Credit Card",
            provider_id=PaymentMethod.PROVIDER_STRIPE,
            is_active=True,
        )
        self.crypto_method = PaymentMethod.objects.create(
            name="Crypto",
            provider_id=PaymentMethod.PROVIDER_NOWPAYMENTS,
            is_active=True,
        )

    def test_payment_factory(self):
        stripe_provider = PaymentFactory.get_provider(PaymentMethod.PROVIDER_STRIPE)
        self.assertIsInstance(stripe_provider, StripeProvider)

        crypto_provider = PaymentFactory.get_provider(
            PaymentMethod.PROVIDER_NOWPAYMENTS
        )
        self.assertIsInstance(crypto_provider, NowPaymentsProvider)

        with self.assertRaises(ValueError):
            PaymentFactory.get_provider("unknown")

    def test_payment_method_toggling(self):
        active_methods = PaymentMethod.objects.filter(is_active=True)
        self.assertEqual(active_methods.count(), 2)

        self.stripe_method.is_active = False
        self.stripe_method.save()

        active_methods = PaymentMethod.objects.filter(is_active=True)
        self.assertEqual(active_methods.count(), 1)
        self.assertEqual(
            active_methods.first().provider_id, PaymentMethod.PROVIDER_NOWPAYMENTS
        )
