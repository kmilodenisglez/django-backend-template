from django.contrib import admin

from .models import Discount, PaymentMethod, Plan, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "currency", "duration_months", "is_active")
    list_filter = ("is_active", "currency")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ("name", "duration_months", "percentage_off", "is_active")
    list_filter = ("is_active",)
    ordering = ("duration_months",)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "plan",
        "status",
        "start_date",
        "end_date",
        "payment_method",
        "is_active",
    )
    list_filter = ("status", "plan", "payment_method", "start_date")
    search_fields = (
        "user__username",
        "user__email",
        "external_id",
        "stripe_subscription_id",
    )
    readonly_fields = (
        "start_date",
        "external_id",
        "stripe_subscription_id",
        "stripe_customer_id",
    )


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ("name", "provider_id", "is_active")
    list_filter = ("is_active", "provider_id")
    search_fields = ("name",)
