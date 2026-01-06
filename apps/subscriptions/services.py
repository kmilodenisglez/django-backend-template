import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import requests
import stripe
from django.conf import settings
from django.core.cache import cache
from django.urls import reverse
from django_settings_env import Env

from .models import PaymentMethod, Subscription

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY

env = Env()


class PaymentProvider(ABC):
    """
    Abstract base class for payment providers.
    """

    @abstractmethod
    def create_checkout_session(self, plan, user, request):
        """
        Creates a checkout session and returns the redirect URL.
        """
        pass

    @abstractmethod
    def handle_webhook(self, request):
        """
        Handles webhook events from the provider.
        """
        pass


class StripeProvider(PaymentProvider):
    """
    Stripe implementation of PaymentProvider.
    """

    def create_checkout_session(self, plan, user, request):
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": plan.stripe_price_id,
                    "quantity": 1,
                },
            ],
            mode="subscription",
            success_url=request.build_absolute_uri(reverse("subscriptions:success"))
            + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.build_absolute_uri(reverse("subscriptions:pricing")),
            customer_email=user.email,
            metadata={
                "user_id": user.id,
                "plan_id": plan.id,
                "provider": "stripe",
            },
        )
        return checkout_session.url

    def handle_webhook(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            return False
        except stripe.error.SignatureVerificationError:
            return False

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            self._handle_checkout_session(session)
        elif event["type"] == "customer.subscription.deleted":
            subscription = event["data"]["object"]
            self._handle_subscription_deleted(subscription)

        return True

    def _handle_checkout_session(self, session):
        user_id = session["metadata"].get("user_id")
        plan_id = session["metadata"].get("plan_id")
        stripe_subscription_id = session["subscription"]
        stripe_customer_id = session["customer"]

        from django.contrib.auth import get_user_model

        from .models import Plan

        User = get_user_model()

        try:
            user = User.objects.get(id=user_id)
            plan = Plan.objects.get(id=plan_id)
            payment_method = PaymentMethod.objects.filter(
                provider_id=PaymentMethod.PROVIDER_STRIPE
            ).first()

            Subscription.objects.create(
                user=user,
                plan=plan,
                payment_method=payment_method,
                external_id=stripe_subscription_id,
                stripe_subscription_id=stripe_subscription_id,
                stripe_customer_id=stripe_customer_id,
                status=Subscription.STATUS_ACTIVE,
            )
        except Exception as e:
            print(f"Error handling Stripe checkout: {e}")

    def _handle_subscription_deleted(self, stripe_subscription):
        stripe_subscription_id = stripe_subscription["id"]
        try:
            sub = Subscription.objects.get(external_id=stripe_subscription_id)
            sub.status = Subscription.STATUS_CANCELED
            sub.save()
        except Subscription.DoesNotExist:
            pass


class NowPaymentsAPI:
    API_BASE = "https://api.nowpayments.io/v1/"

    def __init__(self, token):
        if not token:
            raise ValueError("API key is not specified")
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({"x-api-key": self.token})

    def _call(
        self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make an API call to NowPayments.

        Args:
            method: HTTP method (GET or POST)
            endpoint: API endpoint path
            data: Request data (params for GET, body for POST)

        Returns:
            JSON response as dictionary

        Raises:
            ValueError: If method is not GET or POST
            requests.exceptions.RequestException: If API call fails
        """
        url = f"{self.API_BASE}{endpoint}"

        try:
            if method == "GET":
                response = self.session.get(url, params=data)
            elif method == "POST":
                response = self.session.post(url, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(
                f"NowPayments API Error ({method} {endpoint}): {e}",
                exc_info=True,
            )
            if hasattr(e, "response") and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise

    def status(self) -> Dict[str, Any]:
        """Get API status."""
        return self._call("GET", "status")

    def get_currencies(self) -> Dict[str, Any]:
        """Get list of all available currencies."""
        return self._call("GET", "currencies")

    def get_merchant_coins(self) -> Dict[str, Any]:
        """Return the merchant-configured coins available for this account.

        Returns coins you configured in your merchant dashboard.

        Returns:
            Dictionary with 'selectedCurrencies' key containing list of enabled currencies
        """
        return self._call("GET", "merchant/coins")

    def get_estimate_price(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get estimated price for conversion.

        Args:
            params: Dictionary with 'amount', 'currency_from', 'currency_to'

        Returns:
            Dictionary with estimated conversion amount
        """
        return self._call("GET", "estimate", params)

    def create_payment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a payment."""
        return self._call("POST", "payment", params)

    def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """Get payment status."""
        return self._call("GET", f"payment/{payment_id}")

    def get_minimum_payment_amount(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get minimum payment amount.

        Args:
            params: Dictionary with 'currency_from', 'currency_to'

        Returns:
            Dictionary with 'min_amount' key
        """
        return self._call("GET", "min-amount", params)

    def get_list_payments(
        self, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get list of payments."""
        return self._call("GET", "payment", params)

    def create_invoice(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create an invoice.

        Args:
            params: Dictionary with 'price_amount', 'price_currency', 'pay_currency', etc.

        Returns:
            Dictionary with invoice data including 'invoice_url'
        """
        return self._call("POST", "invoice", params)

    def get_merchant_coins_enriched(
        self,
        merchant_ttl: int = 60,
        full_ttl: int = 60 * 60 * 24,
        cache_key_merchant: str = "nowpayments:merchant_currencies_enriched",
        cache_key_full: str = "nowpayments:full_currencies",
    ) -> List[Dict[str, Any]]:
        """Return merchant-configured coins enriched with data from full-currencies.

        Strategy:
        - Fetch merchant/coins (cheap) to get the list of enabled codes.
        - Try to get enriched data from cache; if not present, call full-currencies once
          and cache it for a long TTL.
        - Merge merchant list with full-currencies by matching code/ticker/name.
        - Cache the enriched merchant list for a short TTL (merchant_ttl).

        Returns a list of dicts with keys: `code`, `name`, `network`, `logo_url`, and
        the original `raw` entry from full-currencies when available.
        """
        cached = cache.get(cache_key_merchant)
        if cached is not None:
            return cached

        try:
            merchant_data = self.get_merchant_coins()
        except Exception:
            cache.set(cache_key_merchant, [], merchant_ttl)
            return []

        # Normalize merchant list similar to views._get_merchant_currencies
        if isinstance(merchant_data, dict) and "selectedCurrencies" in merchant_data:
            available = merchant_data.get("selectedCurrencies", [])
        elif isinstance(merchant_data, list):
            available = merchant_data
        else:
            available = []

        def norm(s: str) -> str:
            return "".join(c for c in str(s).lower() if c.isalnum())

        # Build unique merchant codes preserving original strings
        seen = set()
        merchant_codes: List[str] = []
        for entry in available:
            code = None
            if isinstance(entry, dict):
                code = (
                    entry.get("pay_currency")
                    or entry.get("code")
                    or entry.get("currency")
                    or entry.get("symbol")
                    or entry.get("name")
                )
            else:
                code = entry
            if not code:
                continue
            n = norm(code)
            if n not in seen:
                seen.add(n)
                merchant_codes.append(code)

        if not merchant_codes:
            cache.set(cache_key_merchant, [], merchant_ttl)
            return []

        # Load (or fetch) full currencies mapping once
        full = cache.get(cache_key_full)
        if full is None:
            try:
                full_resp = self._call("GET", "full-currencies")
                # API returns {"currencies": [...]} per example
                full_list = (
                    full_resp.get("currencies") if isinstance(full_resp, dict) else None
                )
                if not isinstance(full_list, list):
                    full_list = []
            except Exception:
                full_list = []
            # Build index by several keys for lenient matching
            mapping: Dict[str, Dict[str, Any]] = {}
            for item in full_list:
                try:
                    code = item.get("code")
                    ticker = item.get("ticker")
                    name = item.get("name")
                    cg_id = item.get("cg_id")
                    for k in (code, ticker, name, cg_id):
                        if k:
                            mapping[
                                "".join(c for c in str(k).lower() if c.isalnum())
                            ] = item
                except Exception:
                    continue
            full = mapping
            # Cache mapping for a long TTL since it's expensive
            cache.set(cache_key_full, full, full_ttl)

        enriched: List[Dict[str, Any]] = []
        for code in merchant_codes:
            key = norm(code)
            matched = full.get(key)
            if not matched:
                # Try uppercase variants or ticker matching fallback
                matched = None
                # additional attempts: try exact uppercase code match
                for k, v in full.items():
                    if k == key:
                        matched = v
                        break
            if matched:
                logo = matched.get("logo_url")
                if logo and isinstance(logo, str) and logo.startswith("/"):
                    logo_url = f"https://nowpayments.io{logo}"
                else:
                    logo_url = logo
                enriched.append(
                    {
                        "code": code,
                        "name": matched.get("name") or code,
                        "network": matched.get("network"),
                        "logo_url": logo_url,
                        "raw": matched,
                    }
                )
            else:
                enriched.append(
                    {
                        "code": code,
                        "name": code,
                        "network": None,
                        "logo_url": None,
                        "raw": None,
                    }
                )

        cache.set(cache_key_merchant, enriched, merchant_ttl)
        return enriched


class NowPaymentsProvider(PaymentProvider):
    """
    NowPayments implementation for Crypto (USDT).
    """

    API_URL = "https://api.nowpayments.io/v1"

    def __init__(self) -> None:
        """Initialize NowPayments provider with API key from environment."""
        self.api_key: Any = env("NOWPAYMENTS_API_KEY")
        if not self.api_key:
            logger.warning(
                "NOWPAYMENTS_API_KEY not configured; crypto payments will be unavailable"
            )

    def get_api(self) -> NowPaymentsAPI:
        """Get or create NowPaymentsAPI instance."""
        return NowPaymentsAPI(self.api_key)

    def create_checkout_session(self, plan: Any, user: Any, request: Any) -> str:
        """Create a checkout session (redirects to crypto selection)."""
        return reverse("subscriptions:crypto_selection", kwargs={"plan_id": plan.id})

    def handle_webhook(self, request: Any) -> bool:
        """Handle NowPayments webhook callback.

        Args:
            request: Django request object with IPN data

        Returns:
            True if webhook was processed successfully, False otherwise
        """
        # Verify IPN signature here
        sig_header = request.META.get("HTTP_X_NOWPAYMENTS_SIG")
        if not sig_header:
            logger.warning("NowPayments webhook missing signature header")
            return False

        # TODO: Implement signature verification using hmac and the IPN secret
        # secret = settings.NOWPAYMENTS_IPN_SECRET

        try:
            data = json.loads(request.body)
            payment_status = data.get("payment_status")
            order_id = data.get(
                "order_id"
            )  # Format: "plan_{id}_month_user_{id}_{timestamp}"
            payment_id = data.get("payment_id")

            if payment_status in ["finished", "confirmed"]:
                # Parse order_id to get user and plan
                parts = order_id.split("_")
                if len(parts) >= 4 and parts[0] == "plan" and parts[2] == "user":
                    plan_id = parts[1]
                    user_id = parts[3]

                    from django.contrib.auth import get_user_model

                    from .models import Plan

                    User = get_user_model()

                    user = User.objects.get(id=user_id)
                    plan = Plan.objects.get(id=plan_id)
                    payment_method = PaymentMethod.objects.filter(
                        provider_id=PaymentMethod.PROVIDER_NOWPAYMENTS
                    ).first()

                    # Check if subscription already exists for this payment
                    if not Subscription.objects.filter(
                        external_id=str(payment_id)
                    ).exists():
                        Subscription.objects.create(
                            user=user,
                            plan=plan,
                            payment_method=payment_method,
                            external_id=str(payment_id),
                            status=Subscription.STATUS_ACTIVE,
                        )
                        logger.info(
                            f"Created subscription for user {user_id} via NowPayments"
                        )

            return True
        except Exception as e:
            logger.error(f"Error handling NowPayments webhook: {e}", exc_info=True)
            return False


class PaymentFactory:
    """Factory for creating payment provider instances."""

    @staticmethod
    def get_provider(provider_id: str) -> PaymentProvider:
        """Get a payment provider instance.

        Args:
            provider_id: Provider identifier (e.g., 'stripe', 'nowpayments')

        Returns:
            PaymentProvider instance

        Raises:
            ValueError: If provider_id is unknown
        """
        if provider_id == PaymentMethod.PROVIDER_STRIPE:
            return StripeProvider()
        elif provider_id == PaymentMethod.PROVIDER_NOWPAYMENTS:
            return NowPaymentsProvider()
        else:
            raise ValueError(f"Unknown provider: {provider_id}")
