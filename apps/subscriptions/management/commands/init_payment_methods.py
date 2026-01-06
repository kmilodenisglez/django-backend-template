from django.core.management.base import BaseCommand

from apps.subscriptions.models import PaymentMethod


class Command(BaseCommand):
    help = "Initialize default payment methods"

    def handle(self, *args, **options):
        methods = [
            {
                "name": "Credit Card (Stripe)",
                "provider_id": PaymentMethod.PROVIDER_STRIPE,
                "is_active": True,
            },
            {
                "name": "Crypto (NowPayments)",
                "provider_id": PaymentMethod.PROVIDER_NOWPAYMENTS,
                "is_active": True,
            },
        ]

        for method_data in methods:
            obj, created = PaymentMethod.objects.get_or_create(
                provider_id=method_data["provider_id"], defaults=method_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Created payment method: {obj.name}")
                )
            else:
                self.stdout.write(f"Payment method already exists: {obj.name}")
