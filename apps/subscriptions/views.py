import json
import logging
from typing import Any, Dict, List, Optional, Union

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt

from .models import PaymentMethod, Plan
from .services import (
    NowPaymentsAPI,
    NowPaymentsProvider,
    PaymentFactory,
    StripeProvider,
)

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


# Get merchant-configured payment currencies
def _get_merchant_currencies(api: NowPaymentsAPI) -> List[str]:
    """Return a list of merchant-configured currency codes.

    Returns the currencies configured in the merchant dashboard for this account.
    Results are cached briefly to avoid API spamming.

    Args:
        api: NowPaymentsAPI instance

    Returns:
        List of available currency codes
    """
    cache_key = "nowpayments:merchant_currencies"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        currencies_data = api.get_merchant_coins()
        # merchant/coins returns selectedCurrencies (list) or a list directly
        if (
            isinstance(currencies_data, dict)
            and "selectedCurrencies" in currencies_data
        ):
            available: List[Union[str, Dict[str, Any]]] = currencies_data.get(
                "selectedCurrencies", []
            )
        elif isinstance(currencies_data, list):
            available = currencies_data
        else:
            available = []
    except Exception as e:
        logger.warning(f"Failed to fetch merchant currencies: {e}")
        cache.set(cache_key, [], 30)
        return []

    def norm(s: str) -> str:
        """Normalize currency code: lowercase and alphanumeric only."""
        return "".join(c for c in str(s).lower() if c.isalnum())

    matched: List[str] = []
    seen: set[str] = set()
    for entry in available:
        code: Optional[str] = None
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
        normalized = norm(code)
        if normalized not in seen:
            seen.add(normalized)
            # Keep original code string returned by provider where possible
            matched.append(code)

    cache.set(cache_key, matched, 60)
    return matched


@login_required
def pricing_page(request):
    plans = Plan.objects.filter(is_active=True).order_by("price")
    active_methods = PaymentMethod.objects.filter(is_active=True)
    return render(
        request,
        "subscriptions/pricing.html",
        {"plans": plans, "payment_methods": active_methods},
    )


@login_required
def create_checkout_session(request: Any, plan_id: int) -> HttpResponse:
    plan = get_object_or_404(Plan, id=plan_id)

    # Get selected provider from query param or form data, default to Stripe if not specified
    provider_id: Optional[str] = request.GET.get(
        "provider", request.POST.get("provider")
    )

    # If no provider specified, check active methods
    if not provider_id:
        active_methods = PaymentMethod.objects.filter(is_active=True)
        if active_methods.count() == 1:
            first_method = active_methods.first()
            if first_method is not None:
                provider_id = first_method.provider_id
        if not provider_id:
            # If multiple methods and none selected, redirect back to pricing or a selection page
            messages.error(request, _("Please select a payment method."))
            return redirect("subscriptions:pricing")

    try:
        provider = PaymentFactory.get_provider(provider_id)
        redirect_url = provider.create_checkout_session(plan, request.user, request)
        return redirect(redirect_url)
    except Exception as e:
        messages.error(request, _("Error creating checkout session: %s") % str(e))
        return redirect("subscriptions:pricing")


@login_required
def success_view(request):
    session_id = request.GET.get("session_id")
    if session_id:
        messages.success(request, _("Subscription successful! Welcome aboard."))
    return redirect("classifieds:user_profile", username=request.user.username)


@csrf_exempt
def stripe_webhook(request):
    # Use the StripeProvider to handle the webhook
    provider = StripeProvider()
    if provider.handle_webhook(request):
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=400)


@csrf_exempt
def nowpayments_webhook(request):
    # Placeholder for NowPayments webhook
    return HttpResponse(status=200)


@login_required
def crypto_payment_selection(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)
    # Query provider for merchant-configured currencies
    provider = NowPaymentsProvider()
    # If the provider isn't configured, inform the user instead of raising
    if not getattr(provider, "api_key", None):
        messages.error(
            request,
            _(
                "Payment provider is not configured. Please contact the site administrator."
            ),
        )
        currencies = []
        return render(
            request,
            "subscriptions/crypto_selection.html",
            {"plan": plan, "currencies": currencies},
        )

    api = provider.get_api()

    # Get enriched merchant-configured currencies (includes name, network, logo)
    try:
        currencies = api.get_merchant_coins_enriched()
    except Exception as e:
        logger.warning(f"Failed to fetch enriched merchant currencies: {e}")
        currencies = []

    if not currencies:
        messages.error(
            request,
            _(
                "No payment currencies are currently available from the payment provider."
            ),
        )
        currencies = []

    return render(
        request,
        "subscriptions/crypto_selection.html",
        {"plan": plan, "currencies": currencies},
    )


@login_required
def get_crypto_estimate(request):
    plan_id = request.GET.get("plan_id")
    if not plan_id:
        return HttpResponse(status=400)

    provider = NowPaymentsProvider()
    if not getattr(provider, "api_key", None):
        return HttpResponse(
            json.dumps({"error": str(_("Payment provider not configured"))}),
            status=400,
            content_type="application/json",
        )

    api = provider.get_api()

    # Use enriched merchant coins to validate and resolve codes
    try:
        currencies_enriched = api.get_merchant_coins_enriched()
    except Exception as e:
        logger.warning(f"Failed to fetch enriched merchant currencies: {e}")
        currencies_enriched = []

    if not currencies_enriched:
        return HttpResponse(
            json.dumps({"error": str(_("No currencies supported by provider"))}),
            status=400,
            content_type="application/json",
        )

    # Allow client to request a specific currency; default to the first available
    requested = request.GET.get("currency")

    def norm(s: str) -> str:
        return "".join(c for c in str(s).lower() if c.isalnum())

    if requested:
        req_norm = norm(requested)
        chosen = None
        for item in currencies_enriched:
            code = item["code"] if isinstance(item, dict) else item
            if norm(code) == req_norm:
                chosen = code
                break
            # also allow matching by name
            name = item.get("name") if isinstance(item, dict) else None
            if name and norm(name) == req_norm:
                chosen = code
                break
        if not chosen:
            return HttpResponse(
                json.dumps({"error": str(_("Requested currency is not available"))}),
                status=400,
                content_type="application/json",
            )
        currency = chosen
    else:
        # default: first merchant code
        first_item = currencies_enriched[0]
        currency = first_item["code"] if isinstance(first_item, dict) else first_item

    plan = get_object_or_404(Plan, id=plan_id)

    try:
        # Get minimum amount
        min_amount_data = api.get_minimum_payment_amount(
            {
                "currency_from": currency,
                "currency_to": plan.currency.lower(),  # Assuming plan currency is fiat like 'usd'
            }
        )
        min_amount = min_amount_data.get("min_amount", 0)

        # Get estimate
        estimate_data = api.get_estimate_price(
            {
                "amount": float(plan.price),
                "currency_from": plan.currency.lower(),
                "currency_to": currency,
            }
        )
        estimated_amount = estimate_data.get("estimated_amount", 0)

        return HttpResponse(
            json.dumps(
                {
                    "min_amount": min_amount,
                    "estimated_amount": estimated_amount,
                    "currency": currency,
                }
            ),
            content_type="application/json",
        )
    except Exception as e:
        return HttpResponse(
            json.dumps({"error": str(e)}), status=500, content_type="application/json"
        )


@login_required
def create_crypto_invoice(request):
    if request.method != "POST":
        return HttpResponse(status=405)

    plan_id = request.POST.get("plan_id")
    plan = get_object_or_404(Plan, id=plan_id)
    user = request.user

    provider = NowPaymentsProvider()
    if not getattr(provider, "api_key", None):
        messages.error(
            request,
            _(
                "Payment provider is not configured. Please contact the site administrator."
            ),
        )
        return redirect("subscriptions:crypto_selection", plan_id=plan_id)

    api: NowPaymentsAPI = provider.get_api()

    # Use enriched merchant coins to validate and resolve codes
    try:
        currencies_enriched = api.get_merchant_coins_enriched()
    except Exception as e:
        logger.warning(f"Failed to fetch enriched merchant currencies: {e}")
        currencies_enriched = []

    if not currencies_enriched:
        messages.error(request, _("No payment currencies are available right now."))
        return redirect("subscriptions:crypto_selection", plan_id=plan_id)

    requested = request.POST.get("currency")

    def norm(s: str) -> str:
        return "".join(c for c in str(s).lower() if c.isalnum())

    if requested:
        req_norm = norm(requested)
        chosen = None
        for item in currencies_enriched:
            code = item["code"] if isinstance(item, dict) else item
            if norm(code) == req_norm:
                chosen = code
                break
            name = item.get("name") if isinstance(item, dict) else None
            if name and norm(name) == req_norm:
                chosen = code
                break
        if not chosen:
            messages.error(request, _("Selected currency is not supported."))
            return redirect("subscriptions:crypto_selection", plan_id=plan_id)
        currency = chosen
    else:
        first_item = currencies_enriched[0]
        currency = first_item["code"] if isinstance(first_item, dict) else first_item

    try:
        # Create invoice
        invoice_data = api.create_invoice(
            {
                "price_amount": float(plan.price),
                "price_currency": plan.currency.lower(),
                "pay_currency": currency,
                "ipn_callback_url": request.build_absolute_uri(
                    reverse("subscriptions:webhook_nowpayments")
                ),
                "order_id": f"plan_{plan_id}_month_user_{user.id}_{timezone.now().timestamp()}",
                "order_description": f"Subscription to {plan.name}",
                "success_url": request.build_absolute_uri(
                    reverse("subscriptions:success")
                ),
                "cancel_url": request.build_absolute_uri(
                    reverse("subscriptions:pricing")
                ),
            }
        )

        invoice_url = invoice_data.get("invoice_url")
        if invoice_url:
            return redirect(invoice_url)
        else:
            messages.error(request, _("Failed to create invoice."))
            return redirect("subscriptions:crypto_selection", plan_id=plan_id)

    except Exception as e:
        messages.error(request, _("Error creating invoice: %s") % str(e))
        return redirect("subscriptions:crypto_selection", plan_id=plan_id)
