from typing import Optional

from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache

from .models import RoleImageLimit, RoleTextLimit, SiteConfiguration


def _determine_effective_role(user) -> str:
    """Return a canonical role name for a given user.

    Order of detection:
    - Anonymous users -> 'Anonymous'
    - superuser -> 'Admin'
    - staff -> 'Staff'
    - profile.subscription_type if provided
    - group name heuristics (SubscriberPaid, Moderator, Staff, Admin, RegisteredFree)
    - fallback -> 'RegisteredFree'
    """
    if (
        not user
        or isinstance(user, AnonymousUser)
        or getattr(user, "is_anonymous", False)
    ):
        return "Anonymous"

    if getattr(user, "is_superuser", False):
        return "Admin"
    if getattr(user, "is_staff", False):
        return "Staff"

    subscription_type = getattr(
        getattr(user, "profile", None), "subscription_type", None
    )
    if subscription_type:
        return subscription_type

    try:
        group_names = list(user.groups.values_list("name", flat=True))
    except Exception:
        group_names = []

    for g in group_names:
        if not g:
            continue
        gl = g.lower()
        if "subscriber" in gl or "paid" in gl:
            return "SubscriberPaid"
        if "moderator" in gl:
            return "Moderator"
        if gl == "staff":
            return "Staff"
        if "admin" in gl or "administrator" in gl:
            return "Admin"
        if "free" in gl or "registered" in gl:
            return "RegisteredFree"

    return "RegisteredFree"


def get_user_text_limits(user) -> dict:
    """Return a dict with 'title' and 'body' limits for the given user, loading from DB.

    Falls back to sensible defaults if DB rows are missing.
    """
    effective_role = _determine_effective_role(user)
    try:
        rl = RoleTextLimit.objects.get(role_name__iexact=effective_role)
        return {"title": rl.title_limit, "body": rl.body_limit}
    except RoleTextLimit.DoesNotExist:
        try:
            # fallback to RegisteredFree
            rl = RoleTextLimit.objects.get(role_name__iexact="RegisteredFree")
            return {"title": rl.title_limit, "body": rl.body_limit}
        except RoleTextLimit.DoesNotExist:
            # last resort: use hard-coded defaults
            return {"title": 200, "body": 2000}


def get_config() -> Optional[SiteConfiguration]:
    """
    Returns the singleton SiteConfiguration instance, cached for 5 minutes.
    """
    config = cache.get("site_config_singleton")
    if config is None:
        try:
            config = SiteConfiguration.objects.first()
            cache.set("site_config_singleton", config, 300)  # 5 minutes
        except Exception:
            config = None
    return config


def get_user_image_limit(user) -> int:
    """
    Returns the max images per ad for the given user based on their role/subscription.
    If user is anonymous or missing data, returns the 'free' limit.
    """
    # Anonymous users: allow creating ads but limit to 5 images (distinct from RegisteredFree)
    if (
        not user
        or isinstance(user, AnonymousUser)
        or getattr(user, "is_anonymous", False)
    ):
        return 5

    # Determine effective role name using multiple signals (in order):
    # 1) superuser -> Admin
    # 2) staff -> Staff
    # 3) profile.subscription_type (if present)
    # 4) group names (SubscriberPaid, Moderator, Staff, Admin)
    # 5) fallback -> RegisteredFree

    # For registered users, default to RegisteredFree unless another role is detected
    else:
        if getattr(user, "is_superuser", False):
            effective_role = "Admin"
        elif getattr(user, "is_staff", False):
            effective_role = "Staff"
        else:
            subscription_type = getattr(
                getattr(user, "profile", None), "subscription_type", None
            )
            if subscription_type:
                effective_role = subscription_type
            else:
                # Inspect groups for common role names
                effective_role = None
                try:
                    group_names = list(user.groups.values_list("name", flat=True))
                except Exception:
                    group_names = []

                for g in group_names:
                    if not g:
                        continue
                    g_low = g.lower()
                    if "subscriber" in g_low or "paid" in g_low:
                        effective_role = "SubscriberPaid"
                        break
                    if "moderator" in g_low:
                        effective_role = "Moderator"
                        break
                    if g_low == "staff":
                        effective_role = "Staff"
                        break
                    if "admin" in g_low or "administrator" in g_low:
                        effective_role = "Admin"
                        break
                    if "free" in g_low or "registered" in g_low:
                        effective_role = "RegisteredFree"
                        break

                if not effective_role:
                    effective_role = "RegisteredFree"

    # Lookup role limit (case-insensitive). Fall back to RegisteredFree, then a hard default.
    try:
        limit_obj = RoleImageLimit.objects.get(role_name__iexact=effective_role)
        return limit_obj.max_images
    except RoleImageLimit.DoesNotExist:
        try:
            return RoleImageLimit.objects.get(
                role_name__iexact="RegisteredFree"
            ).max_images
        except RoleImageLimit.DoesNotExist:
            # As a last resort, try site-wide configuration then a hard-coded default
            try:
                cfg = SiteConfiguration.objects.first()
                if cfg and getattr(cfg, "max_images_per_ad", None):
                    return cfg.max_images_per_ad
            except Exception:
                pass
            return 5
