# Subscription System Documentation

## Overview

The subscription system in Isowo is designed to be modular and extensible, supporting multiple payment providers and flexible plan configurations. It resides in the `apps.subscriptions` application.

## 🏗 Architecture

### Models

- **`Plan`**: Defines subscription tiers (e.g., Monthly, Annual). Contains pricing, duration, and Stripe Price ID.
- **`Discount`**: Defines automatic percentage discounts based on subscription duration.
- **`Subscription`**: Tracks the user's subscription status, start/end dates, and links to the `PaymentMethod` used.
- **`PaymentMethod`**: Configuration model to enable/disable payment providers (Stripe, Crypto) dynamically from the Admin panel.

### Payment Strategy

The system uses a **Strategy Pattern** to handle different payment providers uniformly.

- **`PaymentProvider` (Abstract Base Class)**: Defined in `apps/subscriptions/services.py`. All providers must implement:
    - `create_checkout_session(plan, user, request)`: Returns the redirect URL for payment.
    - `handle_webhook(request)`: Processes provider-specific webhook events.

- **`PaymentFactory`**: A factory class that returns the appropriate `PaymentProvider` instance based on the `provider_id`.

## 💳 Supported Providers

### 1. Stripe (`provider_id="stripe"`)
- **Integration**: Uses `stripe` Python library.
- **Flow**: Creates a Stripe Checkout Session.
- **Webhooks**: Listens for `checkout.session.completed` and `customer.subscription.deleted`.

### 2. Crypto / NowPayments (`provider_id="nowpayments"`)
- **Integration**: Uses NowPayments API (currently mocked/simplified).
- **Flow**: Generates an invoice URL (or mock URL).
- **Currency**: Configured for USDT (TRC20).

## ⚙️ Configuration

### Environment Variables

Ensure these variables are set in your `.env` file:

```env
# Stripe
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# NowPayments (Optional)
NOWPAYMENTS_API_KEY=your-api-key
```

### Admin Configuration

1.  **Plans**: Create plans in `/admin/subscriptions/plan/`.
2.  **Payment Methods**: Enable/Disable providers in `/admin/subscriptions/paymentmethod/`.
    - Run `python manage.py init_payment_methods` to create defaults.

## 🚀 Adding a New Provider

1.  Add a new constant to `PaymentMethod.PROVIDER_CHOICES` in `models.py`.
2.  Create a new provider class inheriting from `PaymentProvider` in `services.py`.
3.  Update `PaymentFactory` to return your new provider.
4.  Add a webhook endpoint in `views.py` and `urls.py` if needed.
