from django.urls import path

from . import views

app_name = "subscriptions"

urlpatterns = [
    path("pricing/", views.pricing_page, name="pricing"),
    path(
        "checkout/<int:plan_id>/",
        views.create_checkout_session,
        name="create_checkout_session",
    ),
    path("success/", views.success_view, name="success"),
    path("webhook/", views.stripe_webhook, name="webhook"),
    path("webhook/nowpayments/", views.nowpayments_webhook, name="webhook_nowpayments"),
    path(
        "crypto/select/<int:plan_id>/",
        views.crypto_payment_selection,
        name="crypto_selection",
    ),
    path("crypto/estimate/", views.get_crypto_estimate, name="get_crypto_estimate"),
    path("crypto/invoice/", views.create_crypto_invoice, name="create_crypto_invoice"),
]
