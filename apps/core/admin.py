from django import forms
from django.contrib import admin

from .admin_mixins import SingletonModelAdminMixin
from .models import RoleImageLimit, RoleTextLimit, SiteConfiguration


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(SingletonModelAdminMixin, admin.ModelAdmin):
    list_display = ("site_name", "contact_email", "max_images_per_ad", "updated_at")
    readonly_fields = ("updated_at",)


@admin.register(RoleImageLimit)
class RoleImageLimitAdmin(admin.ModelAdmin):
    list_display = ("role_name", "max_images")
    search_fields = ("role_name",)
    ordering = ("role_name",)


class RoleTextLimitForm(forms.ModelForm):
    class Meta:
        model = RoleTextLimit
        fields = ("role_name", "title_limit", "body_limit")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[
            "title_limit"
        ].help_text = "Maximum characters allowed for the ad title (1-1000)."
        self.fields[
            "body_limit"
        ].help_text = "Maximum characters allowed for the ad body (10-20000)."

    def clean_title_limit(self):
        v = self.cleaned_data.get("title_limit")
        if v is None:
            return v
        if v < 1 or v > 1000:
            raise forms.ValidationError(
                "Title limit must be between 1 and 1000 characters."
            )
        return v

    def clean_body_limit(self):
        v = self.cleaned_data.get("body_limit")
        if v is None:
            return v
        if v < 10 or v > 20000:
            raise forms.ValidationError(
                "Body limit must be between 10 and 20000 characters."
            )
        return v


@admin.register(RoleTextLimit)
class RoleTextLimitAdmin(admin.ModelAdmin):
    form = RoleTextLimitForm
    list_display = ("role_name", "title_limit", "body_limit")
    search_fields = ("role_name",)
    ordering = ("role_name",)
    fieldsets = (
        (None, {"fields": ("role_name",)}),
        ("Limits", {"fields": ("title_limit", "body_limit")}),
    )
