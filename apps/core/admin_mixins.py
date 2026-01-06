from typing import Any, cast

from django.contrib import admin as django_admin
from django.shortcuts import redirect
from django.urls import reverse


class SingletonModelAdminMixin:
    """Admin mixin for singleton models.

    Provides sensible defaults for models where only a single instance should
    exist in the DB (site-wide configuration objects, feature flags, etc.).

    Behavior provided:
    - Hide "Save and add another" and "Save and continue" in the change form
    - Prevent deletion via admin
    - Prevent accessing the add view when an instance exists (redirect to
      the existing instance change view)
    - Redirect the changelist to the single instance change view
    - After creating a new instance, redirect to its change view

    Example
    -------
    Basic usage in ``admin.py``::

        from django.contrib import admin
        from .models import SiteConfiguration
        from .admin_mixins import SingletonModelAdminMixin

        @admin.register(SiteConfiguration)
        class SiteConfigurationAdmin(SingletonModelAdminMixin, admin.ModelAdmin):
            # Admin for SiteConfiguration where only one instance exists.

    The mixin should be listed before ``admin.ModelAdmin`` in the
    inheritance order so its behavior is applied to the admin view.
    """

    # Help static type checkers (pylance/mypy): admin classes set `model` at
    # registration time — declare it here so `self.model` is recognized.
    model: Any

    def has_add_permission(self, request):
        # Only allow add if no instance exists
        return not self.model.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Prevent deleting the singleton from the admin UI
        return False

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context.setdefault("show_save_and_add_another", False)
        extra_context.setdefault("show_save_and_continue", False)
        return django_admin.ModelAdmin.changeform_view(
            cast(django_admin.ModelAdmin, self),
            request,
            object_id,
            form_url,
            extra_context=extra_context,
        )

    def response_add(self, request, obj, post_url_continue=None):
        change_url = reverse(
            f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change",
            args=[obj.pk],
        )
        return redirect(change_url)

    def changelist_view(self, request, extra_context=None):
        config = self.model.objects.first()
        if config is not None:
            return redirect(
                reverse(
                    f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change",
                    args=[config.pk],
                )
            )

        if self.has_add_permission(request):
            return redirect(
                reverse(
                    f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_add"
                )
            )

        return django_admin.ModelAdmin.changelist_view(
            cast(django_admin.ModelAdmin, self), request, extra_context=extra_context
        )

    def add_view(self, request, form_url="", extra_context=None):
        config = self.model.objects.first()
        if config is not None:
            change_url = reverse(
                f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change",
                args=[config.pk],
            )
            return redirect(change_url)

        return django_admin.ModelAdmin.add_view(
            cast(django_admin.ModelAdmin, self),
            request,
            form_url,
            extra_context=extra_context,
        )
