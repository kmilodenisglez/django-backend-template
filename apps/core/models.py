from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class SiteConfiguration(models.Model):
    """
    Singleton model for global site settings (not secrets).
    Only one instance allowed. Use get_config() utility to access.
    """

    site_name = models.CharField(_("Site Name"), max_length=128)
    logo = models.ImageField(_("Logo"), upload_to="site_logo/", blank=True, null=True)
    contact_email = models.EmailField(_("Contact Email"), max_length=254)
    footer_text = models.TextField(_("Footer Text"), blank=True)
    max_images_per_ad = models.PositiveIntegerField(_("Max Images Per Ad"), default=5)
    updated_at = models.DateTimeField(_("Last Updated"), auto_now=True)

    class Meta:
        verbose_name = _("Site Configuration")
        verbose_name_plural = _("Site Configuration")

    def clean(self):
        if SiteConfiguration.objects.exclude(pk=self.pk).exists():
            raise ValidationError(_("Only one SiteConfiguration instance is allowed."))

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        # Invalidate cache on save
        cache.delete("site_config_singleton")

    def __str__(self):
        return self.site_name or _("Site Configuration")


class RoleImageLimit(models.Model):
    """
    Defines max images per ad for each user role/subscription.
    """

    role_name = models.CharField(_("Role Name"), max_length=32, unique=True)
    max_images = models.PositiveIntegerField(_("Max Images"), default=5)

    class Meta:
        verbose_name = _("Role Image Limit")
        verbose_name_plural = _("Role Image Limits")
        ordering = ["role_name"]

    def __str__(self):
        return f"{self.role_name}: {self.max_images} images"

    def clean(self):
        from django.utils.translation import gettext_lazy as _

        if self.max_images is None:
            raise ValidationError({"max_images": _("Max images is required")})
        if self.max_images < 1 or self.max_images > 60:
            raise ValidationError(
                {
                    "max_images": _("Max images must be between 1 and 60."),
                }
            )


class RoleTextLimit(models.Model):
    """
    Stores text length limits (title/body) per role. Allows editable limits per role.
    """

    role_name = models.CharField(_("Role Name"), max_length=32, unique=True)
    title_limit = models.PositiveIntegerField(_("Title Limit"), default=200)
    body_limit = models.PositiveIntegerField(_("Body Limit"), default=2000)

    class Meta:
        verbose_name = _("Role Text Limit")
        verbose_name_plural = _("Role Text Limits")
        ordering = ["role_name"]

    def __str__(self):
        return f"{self.role_name}: title={self.title_limit} body={self.body_limit}"

    def clean(self):
        from django.utils.translation import gettext_lazy as _

        errors = {}
        if self.title_limit is None:
            errors["title_limit"] = _("Title limit is required")
        elif self.title_limit < 1 or self.title_limit > 1000:
            errors["title_limit"] = _(
                "Title limit must be between 1 and 1000 characters."
            )

        if self.body_limit is None:
            errors["body_limit"] = _("Body limit is required")
        elif self.body_limit < 10 or self.body_limit > 20000:
            errors["body_limit"] = _(
                "Body limit must be between 10 and 20000 characters."
            )

        if errors:
            raise ValidationError(errors)
