from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class PaymentMethod(models.Model):
    """
    Configuration for different payment providers (Stripe, Crypto, etc.)
    """

    PROVIDER_STRIPE = "stripe"
    PROVIDER_NOWPAYMENTS = "nowpayments"

    PROVIDER_CHOICES = [
        (PROVIDER_STRIPE, _("Stripe")),
        (PROVIDER_NOWPAYMENTS, _("Crypto (NowPayments)")),
    ]

    name = models.CharField(
        _("Display Name"), max_length=100, help_text=_("e.g. Credit Card, Crypto")
    )
    provider_id = models.CharField(
        _("Provider ID"), max_length=50, choices=PROVIDER_CHOICES, unique=True
    )
    is_active = models.BooleanField(_("Active"), default=True)
    config = models.JSONField(
        _("Configuration"),
        default=dict,
        blank=True,
        help_text=_("Provider specific config (public keys, etc)"),
    )

    class Meta:
        verbose_name = _("Payment Method")
        verbose_name_plural = _("Payment Methods")

    def __str__(self):
        return f"{self.name} ({self.get_provider_id_display()})"


class Plan(models.Model):
    """
    Defines a subscription plan (e.g., Monthly, Annual).
    """

    PERIOD_MONTHLY = "monthly"
    PERIOD_ANNUAL = "annual"
    PERIOD_CHOICES = [
        (PERIOD_MONTHLY, _("Monthly")),
        (PERIOD_ANNUAL, _("Annual")),
    ]

    name = models.CharField(_("Name"), max_length=100)
    slug = models.SlugField(_("Slug"), unique=True)
    price = models.DecimalField(_("Price"), max_digits=10, decimal_places=2)
    currency = models.CharField(_("Currency"), max_length=3, default="USD")
    duration_months = models.PositiveIntegerField(_("Duration (Months)"), default=1)
    stripe_price_id = models.CharField(
        _("Stripe Price ID"), max_length=100, blank=True, null=True
    )
    description = models.TextField(_("Description"), blank=True)
    is_active = models.BooleanField(_("Active"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Plan")
        verbose_name_plural = _("Plans")
        ordering = ["price"]

    def __str__(self):
        return f"{self.name} ({self.get_duration_display()})"

    def get_duration_display(self):
        if self.duration_months == 1:
            return "Monthly"
        elif self.duration_months == 12:
            return "Annual"
        return f"{self.duration_months} Months"


class Discount(models.Model):
    """
    Automatic discounts based on subscription duration.
    """

    name = models.CharField(_("Name"), max_length=100)
    duration_months = models.PositiveIntegerField(
        _("Duration (Months)"),
        unique=True,
        help_text=_("Minimum duration to apply this discount"),
    )
    percentage_off = models.PositiveIntegerField(
        _("Percentage Off"), help_text=_("Discount percentage (0-100)")
    )
    is_active = models.BooleanField(_("Active"), default=True)

    class Meta:
        verbose_name = _("Discount")
        verbose_name_plural = _("Discounts")
        ordering = ["duration_months"]

    def __str__(self):
        return f"{self.name} - {self.percentage_off}% off for {self.duration_months}+ months"


class Subscription(models.Model):
    """
    Tracks a user's subscription status.
    """

    STATUS_ACTIVE = "active"
    STATUS_CANCELED = "canceled"
    STATUS_PAST_DUE = "past_due"
    STATUS_UNPAID = "unpaid"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, _("Active")),
        (STATUS_CANCELED, _("Canceled")),
        (STATUS_PAST_DUE, _("Past Due")),
        (STATUS_UNPAID, _("Unpaid")),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions_new",  # Temporary related_name to avoid conflict during migration if needed
    )
    plan = models.ForeignKey(
        Plan, on_delete=models.SET_NULL, null=True, related_name="subscriptions"
    )
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subscriptions",
    )
    status = models.CharField(
        _("Status"), max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE
    )
    start_date = models.DateTimeField(_("Start Date"), auto_now_add=True)
    end_date = models.DateTimeField(_("End Date"), null=True, blank=True)

    # Generic external ID to support multiple providers (Stripe, NowPayments, etc)
    external_id = models.CharField(
        _("External Subscription ID"),
        max_length=100,
        blank=True,
        null=True,
        help_text=_("ID from the payment provider (e.g. sub_123 or payment_id)"),
    )

    # Kept for backward compatibility but can be deprecated
    stripe_subscription_id = models.CharField(
        _("Stripe Subscription ID"), max_length=100, blank=True, null=True
    )
    stripe_customer_id = models.CharField(
        _("Stripe Customer ID"), max_length=100, blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Subscription")
        verbose_name_plural = _("Subscriptions")
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.user} - {self.plan} ({self.status})"

    @property
    def is_active(self):
        return (
            self.status == self.STATUS_ACTIVE
            and self.end_date
            and self.end_date > timezone.now()
        )
